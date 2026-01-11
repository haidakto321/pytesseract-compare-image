"""
Smart Image Comparison Tool
Compares images focusing on text content and focus elements while ignoring styling differences
"""

import cv2
import numpy as np
from pathlib import Path
import pytesseract
from PIL import Image
import json
from dataclasses import dataclass
from typing import List, Tuple, Dict
import argparse
import shutil

@dataclass
class TextBox:
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float

@dataclass
class Field:
    """Represents a form field with its properties"""
    field_type: str  # 'input', 'checkbox', 'radio', 'dropdown', 'button'
    value: str
    x: int
    y: int
    width: int
    height: int
    text_boxes: List[TextBox]  # All text boxes that make up this field
    
    def __repr__(self):
        return f"Field({self.field_type}, '{self.value}', pos=({self.x},{self.y}))"

@dataclass
class FieldDifference:
    """Represents a difference between two fields"""
    field_type: str
    description: str
    value1: str
    value2: str
    position: Tuple[int, int]  # (x, y)

@dataclass
class ComparisonResult:
    image_name: str
    text_match: bool
    text_differences: List[str]
    focus_match: bool
    focus_details: Dict
    overall_match: bool
    field_differences: List[FieldDifference] = None  # New field for field-level diffs
    
    def __post_init__(self):
        if self.field_differences is None:
            self.field_differences = []

class SmartImageComparator:
    def __init__(self, ignore_case=True, similarity_threshold=1.0, default_crop_percentage=0.12):
        self.ignore_case = ignore_case
        self.similarity_threshold = similarity_threshold
        self.default_crop_percentage = default_crop_percentage
    
    def detect_header_boundary(self, img: np.ndarray, sample_height: int = 20) -> int:
        """
        Detect header bottom boundary by analyzing color uniformity
        Returns the y-coordinate where header ends, or None if detection fails
        """
        try:
            height, width = img.shape[:2]
            
            # Sample top portion for header color analysis
            sample_region = img[0:min(sample_height, height), :]
            
            # Get dominant color from sample (mode of colors)
            # Reshape to list of pixels
            pixels = sample_region.reshape(-1, 3)
            
            # Calculate mean color of sample region
            mean_color = np.mean(pixels, axis=0)
            
            # Define color tolerance (how different a pixel can be from header color)
            color_tolerance = 30
            
            # Scan downward to find where header color ends
            for y in range(sample_height, min(int(height * 0.25), height)):  # Check up to 25% of image
                row = img[y, :]
                row_mean = np.mean(row, axis=0)
                
                # Calculate color difference
                color_diff = np.abs(row_mean - mean_color).sum()
                
                # If row color significantly different from header, we found the boundary
                if color_diff > color_tolerance:
                    # Add small margin (10 pixels) to ensure we're past header
                    return min(y + 10, height)
            
            # If no boundary found, return None (fallback will be used)
            return None
            
        except Exception as e:
            # If detection fails for any reason, return None to use fallback
            print(f"Header detection failed: {e}, using fallback")
            return None
    
    def crop_by_percentage(self, img: np.ndarray, percentage: float = 0.12) -> tuple:
        """
        Crop top percentage of image
        Returns (cropped_image, crop_offset)
        """
        height = img.shape[0]
        crop_height = int(height * percentage)
        cropped = img[crop_height:, :]
        return cropped, crop_height
    
    def smart_crop_header(self, img: np.ndarray) -> tuple:
        """
        Hybrid approach: Try dynamic detection, fallback to percentage
        Returns (cropped_image, crop_offset)
        """
        # Try dynamic header detection
        boundary = self.detect_header_boundary(img)
        
        if boundary is not None and 30 < boundary < img.shape[0] * 0.3:
            # Valid boundary found (between 30px and 30% of image)
            print(f"  → Header detected at y={boundary}px (dynamic detection)")
            return img[boundary:, :], boundary
        else:
            # Fallback to percentage-based cropping
            cropped, offset = self.crop_by_percentage(img, self.default_crop_percentage)
            print(f"  → Header cropped at {self.default_crop_percentage*100:.0f}% = {offset}px (fallback)")
            return cropped, offset
    
    def extract_text_boxes(self, img_path: str) -> List[TextBox]:
        """Extract text boxes with their positions from an image, with smart header removal"""
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Cannot read image: {img_path}")
        
        # Smart crop to remove header
        cropped_img, crop_offset = self.smart_crop_header(img)
        
        # Use pytesseract on cropped image
        data = pytesseract.image_to_data(cropped_img, output_type=pytesseract.Output.DICT)
        
        text_boxes = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            
            # Filter: high confidence only
            if text and int(data['conf'][i]) > 30:
                text_box = TextBox(
                    text=text,
                    x=data['left'][i],
                    y=data['top'][i] + crop_offset,  # Adjust y-coordinate back to original image space
                    width=data['width'][i],
                    height=data['height'][i],
                    confidence=float(data['conf'][i])
                )
                text_boxes.append(text_box)
        
        return text_boxes
    
    def detect_text_cursor(self, img: np.ndarray) -> List[Dict]:
        """Detect text cursor (blinking cursor '|' in input fields)"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Look for vertical thin lines (text cursor)
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        cursors = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Text cursor characteristics
            if w <= 3 and h > w * 3 and 10 < h < 50:
                cursors.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'type': 'text_cursor'
                })
        
        return cursors
    
    def detect_bold_text(self, img: np.ndarray) -> List[Dict]:
        """Detect bolder text which indicates focused element"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get text regions
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bold_areas = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 50000:
                x, y, w, h = cv2.boundingRect(contour)
                
                roi = binary[y:y+h, x:x+w]
                density = np.sum(roi > 0) / (w * h) if w * h > 0 else 0
                
                if density > 0.15:
                    bold_areas.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'density': float(density),
                        'type': 'bold_text'
                    })
        
        return bold_areas
    
    def detect_rounded_borders(self, img: np.ndarray) -> List[Dict]:
        """Detect input fields with rounded borders"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        rounded_borders = []
        for contour in contours:
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            if len(approx) >= 4 and 1000 < area < 100000:
                rect_perimeter = 2 * (w + h)
                contour_perimeter = cv2.arcLength(contour, True)
                
                roundness = contour_perimeter / rect_perimeter if rect_perimeter > 0 else 0
                
                if 1.05 < roundness < 1.3:
                    rounded_borders.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'roundness': float(roundness),
                        'type': 'rounded_border'
                    })
        
        return rounded_borders
    
    def detect_focus_element(self, img_path: str) -> Dict:
        """Detect focused element with smart header removal"""
        img = cv2.imread(img_path)
        if img is None:
            return {}
        
        # Smart crop to remove header
        cropped_img, crop_offset = self.smart_crop_header(img)
        
        # Detect focus elements on cropped image
        cursors = self.detect_text_cursor(cropped_img)
        bold_areas = self.detect_bold_text(cropped_img)
        rounded_borders = self.detect_rounded_borders(cropped_img)
        
        # Adjust y-coordinates back to original image space
        for c in cursors:
            c['y'] += crop_offset
        for b in bold_areas:
            b['y'] += crop_offset
        for r in rounded_borders:
            r['y'] += crop_offset
        
        all_focus_elements = cursors + bold_areas + rounded_borders
        
        priority_order = {'text_cursor': 3, 'rounded_border': 2, 'bold_text': 1}
        all_focus_elements.sort(key=lambda x: priority_order.get(x['type'], 0), reverse=True)
        
        return {
            'focus_elements': all_focus_elements,
            'primary_focus': all_focus_elements[0] if all_focus_elements else None,
            'cursors_found': len(cursors),
            'bold_areas_found': len(bold_areas),
            'rounded_borders_found': len(rounded_borders)
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        text = text.strip()
        if self.ignore_case:
            text = text.lower()
        text = ' '.join(text.split())
        return text
    
    def group_text_boxes_into_fields(self, boxes: List[TextBox]) -> List[Field]:
        """
        Group nearby text boxes into fields based on spatial proximity
        Returns list of detected fields
        """
        if not boxes:
            return []
        
        fields = []
        used_boxes = set()
        
        # Sort boxes by y-coordinate (top to bottom), then x (left to right)
        sorted_boxes = sorted(boxes, key=lambda b: (b.y, b.x))
        
        for box in sorted_boxes:
            if id(box) in used_boxes:
                continue
            
            # Start a new field with this box
            field_boxes = [box]
            used_boxes.add(id(box))
            
            # Find nearby boxes that belong to the same field
            # Look for boxes within reasonable horizontal/vertical distance
            for other_box in sorted_boxes:
                if id(other_box) in used_boxes:
                    continue
                
                # Check if other_box is close to any box in current field
                for field_box in field_boxes:
                    h_distance = abs(other_box.x - (field_box.x + field_box.width))
                    v_distance = abs(other_box.y - field_box.y)
                    
                    # Boxes on same line (similar y) and close horizontally
                    if v_distance < 10 and h_distance < 150:
                        field_boxes.append(other_box)
                        used_boxes.add(id(other_box))
                        break
            
            # Create field from grouped boxes
            field = self._create_field_from_boxes(field_boxes)
            fields.append(field)
        
        return fields
    
    def _create_field_from_boxes(self, boxes: List[TextBox]) -> Field:
        """Create a Field object from grouped text boxes"""
        if not boxes:
            return None
        
        # Calculate bounding box for all text boxes
        min_x = min(b.x for b in boxes)
        min_y = min(b.y for b in boxes)
        max_x = max(b.x + b.width for b in boxes)
        max_y = max(b.y + b.height for b in boxes)
        
        # Combine text from all boxes
        combined_text = ' '.join(b.text for b in boxes)
        
        # Detect field type based on text patterns
        field_type = self._detect_field_type(combined_text, boxes)
        
        return Field(
            field_type=field_type,
            value=combined_text,
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
            text_boxes=boxes
        )
    
    def _detect_field_type(self, text: str, boxes: List[TextBox]) -> str:
        """Detect field type based on text content and patterns"""
        text_lower = text.lower()
        
        # Button patterns
        button_keywords = ['保存', '更新', 'クリア', 'キャンセル', 'save', 'clear', 'cancel', 'submit', '登録']
        if any(keyword in text_lower for keyword in button_keywords):
            return 'button'
        
        # Checkbox patterns (multiple selections)
        checkbox_keywords = ['メルマガ', 'newsletter', '規約', 'terms', '更新情報', 'updates']
        if any(keyword in text_lower for keyword in checkbox_keywords):
            return 'checkbox'
        
        # Radio button patterns (single selection)
        radio_keywords = ['男性', '女性', 'male', 'female', '性別']
        if any(keyword in text_lower for keyword in radio_keywords):
            return 'radio'
        
        # Dropdown patterns (prefecture, options)
        dropdown_keywords = ['東京', '大阪', '愛知', '福岡', '北海道', '都', '府', '県']
        if any(keyword in text_lower for keyword in dropdown_keywords):
            return 'dropdown'
        
        # Email pattern
        if '@' in text or 'mail' in text_lower or 'メール' in text:
            return 'input_email'
        
        # Phone pattern
        if any(c.isdigit() for c in text) and ('-' in text or len([c for c in text if c.isdigit()]) >= 8):
            return 'input_phone'
        
        # Date pattern
        if '/' in text and any(c.isdigit() for c in text):
            return 'input_date'
        
        # Default to input field
        return 'input_text'
    
    def compare_fields(self, fields1: List[Field], fields2: List[Field]) -> List[FieldDifference]:
        """
        Compare two sets of fields and identify semantic differences
        Returns list of field-level differences
        """
        differences = []
        
        # Match fields by position (fields in similar positions are considered the same field)
        matched_pairs = []
        unmatched_1 = list(fields1)
        unmatched_2 = list(fields2)
        
        # Find matching fields by position
        for f1 in fields1:
            best_match = None
            min_distance = float('inf')
            
            for f2 in fields2:
                # Calculate distance between field centers
                center1 = (f1.x + f1.width/2, f1.y + f1.height/2)
                center2 = (f2.x + f2.width/2, f2.y + f2.height/2)
                distance = ((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)**0.5
                
                # Fields are considered same if within 100 pixels
                if distance < 100 and distance < min_distance:
                    min_distance = distance
                    best_match = f2
            
            if best_match:
                matched_pairs.append((f1, best_match))
                if f1 in unmatched_1:
                    unmatched_1.remove(f1)
                if best_match in unmatched_2:
                    unmatched_2.remove(best_match)
        
        # Compare matched fields
        for f1, f2 in matched_pairs:
            if self.normalize_text(f1.value) != self.normalize_text(f2.value):
                diff = FieldDifference(
                    field_type=f1.field_type,
                    description=self._generate_field_diff_description(f1, f2),
                    value1=f1.value,
                    value2=f2.value,
                    position=(f1.x, f1.y)
                )
                differences.append(diff)
        
        # Report unmatched fields (added/removed)
        for f1 in unmatched_1:
            diff = FieldDifference(
                field_type=f1.field_type,
                description=f"Field removed in Version 2: {f1.field_type}",
                value1=f1.value,
                value2="",
                position=(f1.x, f1.y)
            )
            differences.append(diff)
        
        for f2 in unmatched_2:
            diff = FieldDifference(
                field_type=f2.field_type,
                description=f"Field added in Version 2: {f2.field_type}",
                value1="",
                value2=f2.value,
                position=(f2.x, f2.y)
            )
            differences.append(diff)
        
        return differences
    
    def _generate_field_diff_description(self, f1: Field, f2: Field) -> str:
        """Generate human-readable description of field difference"""
        field_type = f1.field_type
        
        if field_type == 'button':
            return f"Button text changed: '{f1.value}' → '{f2.value}'"
        
        elif field_type == 'checkbox':
            # Try to detect which checkbox changed
            words1 = set(f1.value.lower().split())
            words2 = set(f2.value.lower().split())
            added = words2 - words1
            removed = words1 - words2
            
            if added:
                return f"Checkbox: '{', '.join(added)}' checked in Version 2"
            elif removed:
                return f"Checkbox: '{', '.join(removed)}' unchecked in Version 2"
            else:
                return f"Checkbox selection changed"
        
        elif field_type == 'radio':
            return f"Radio button: '{f1.value}' → '{f2.value}'"
        
        elif field_type == 'dropdown':
            # Extract likely dropdown value (prefecture name)
            val1 = f1.value.strip()
            val2 = f2.value.strip()
            return f"Dropdown selection: '{val1}' → '{val2}'"
        
        elif field_type.startswith('input'):
            input_type = field_type.replace('input_', '')
            return f"Input field ({input_type}) changed: '{f1.value}' → '{f2.value}'"
        
        else:
            return f"Field changed: '{f1.value}' → '{f2.value}'"
    
    def compare_text_content(self, boxes1: List[TextBox], boxes2: List[TextBox]) -> Tuple[bool, List[str]]:
        """Compare text content from two sets of text boxes"""
        text1 = sorted([self.normalize_text(box.text) for box in boxes1])
        text2 = sorted([self.normalize_text(box.text) for box in boxes2])
        
        # Filter out very short fragments (likely OCR noise)
        text1_filtered = [t for t in text1 if len(t) >= 2]
        text2_filtered = [t for t in text2 if len(t) >= 2]
        
        differences = []
        
        only_in_1 = [t for t in text1_filtered if t not in text2_filtered]
        if only_in_1:
            # Limit to first 10 items for readability
            display_list = only_in_1[:10]
            suffix = f" ... and {len(only_in_1) - 10} more" if len(only_in_1) > 10 else ""
            differences.append(f"Only in Version 1: {display_list}{suffix}")
        
        only_in_2 = [t for t in text2_filtered if t not in text1_filtered]
        if only_in_2:
            # Limit to first 10 items for readability
            display_list = only_in_2[:10]
            suffix = f" ... and {len(only_in_2) - 10} more" if len(only_in_2) > 10 else ""
            differences.append(f"Only in Version 2: {display_list}{suffix}")
        
        all_texts = set(text1_filtered + text2_filtered)
        matching_texts = set(text1_filtered) & set(text2_filtered)
        
        if not all_texts:
            return True, []
        
        similarity = len(matching_texts) / len(all_texts)
        match = similarity >= self.similarity_threshold
        
        if not match:
            differences.insert(0, f"Text similarity: {similarity:.2%}")
        
        return match, differences
    
    def compare_focus(self, focus1: Dict, focus2: Dict, tolerance: int = 50) -> Tuple[bool, Dict]:
        """Compare focus elements with position tolerance"""
        f1 = focus1.get('primary_focus')
        f2 = focus2.get('primary_focus')
        
        if f1 is None and f2 is None:
            return True, {'message': 'No focus elements detected in either image'}
        
        if f1 is None or f2 is None:
            return False, {
                'message': 'Focus element present in only one image',
                'focus1': f1,
                'focus2': f2
            }
        
        x_diff = abs(f1['x'] - f2['x'])
        y_diff = abs(f1['y'] - f2['y'])
        
        match = x_diff <= tolerance and y_diff <= tolerance
        
        return match, {
            'position_difference': {'x': x_diff, 'y': y_diff},
            'focus1': f1,
            'focus2': f2,
            'tolerance': tolerance
        }
    
    def compare_images(self, img1_path: str, img2_path: str) -> ComparisonResult:
        """Compare two images focusing on text content and focus elements"""
        img_name = Path(img1_path).name
        
        print(f"Processing {img_name}...")
        
        print("  - Extracting text from first image...")
        boxes1 = self.extract_text_boxes(img1_path)
        print(f"    Found {len(boxes1)} text boxes")
        
        print("  - Extracting text from second image...")
        boxes2 = self.extract_text_boxes(img2_path)
        print(f"    Found {len(boxes2)} text boxes")
        
        # Simple text comparison
        text_match, old_text_diffs = self.compare_text_content(boxes1, boxes2)
        
        # Generate clean, simple summary instead of showing OCR fragments
        text_diffs = []
        if not text_match:
            # Calculate similarity for summary
            text1 = sorted([self.normalize_text(box.text) for box in boxes1 if len(box.text) >= 2])
            text2 = sorted([self.normalize_text(box.text) for box in boxes2 if len(box.text) >= 2])
            
            # Simple similarity calculation
            common = len(set(text1) & set(text2))
            total = len(set(text1) | set(text2))
            similarity = (common / total * 100) if total > 0 else 0
            
            # Generate clean message based on similarity
            if similarity >= 95:
                text_diffs.append("Form content has minor differences")
                text_diffs.append("💡 Click images to zoom and inspect details")
            elif similarity >= 80:
                text_diffs.append("Form content differs in several fields")
                text_diffs.append("💡 Click images to zoom and compare")
            elif similarity >= 50:
                text_diffs.append("Form content has significant differences")
                text_diffs.append("💡 Review images carefully - multiple changes detected")
            else:
                text_diffs.append("Major content differences detected")
                text_diffs.append("⚠️ Significant structural or data changes")
                text_diffs.append("💡 Manual review recommended")
        
        print("  - Detecting focus elements...")
        focus1 = self.detect_focus_element(img1_path)
        focus2 = self.detect_focus_element(img2_path)
        focus_match, focus_details = self.compare_focus(focus1, focus2)
        
        overall_match = text_match and focus_match
        
        return ComparisonResult(
            image_name=img_name,
            text_match=text_match,
            text_differences=text_diffs,
            focus_match=focus_match,
            focus_details=focus_details,
            overall_match=overall_match,
            field_differences=[]  # Not used in simple mode
        )

def generate_html_report(results: List[ComparisonResult], folder1: str, folder2: str, 
                         folder1_path: Path, folder2_path: Path, output_html: str = "comparison_report.html"):
    """Generate an HTML report with side-by-side image comparison"""
    
    total = len(results)
    passed = sum(1 for r in results if r.overall_match)
    failed = total - passed
    
    # Create image folder
    html_path = Path(output_html)
    images_folder = html_path.parent / "report_images"
    images_folder.mkdir(exist_ok=True)
    
    v1_folder = images_folder / "version1"
    v2_folder = images_folder / "version2"
    v1_folder.mkdir(exist_ok=True)
    v2_folder.mkdir(exist_ok=True)
    
    # Start building HTML
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('<meta charset="UTF-8">')
    html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('<title>Image Comparison Report</title>')
    html.append('<style>')
    html.append('''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; line-height: 1.6; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .header h1 { font-size: 18px; margin-bottom: 3px; }
        .header p { opacity: 0.9; font-size: 11px; }
        .controls { background: white; padding: 15px 30px; border-bottom: 1px solid #e0e0e0; position: sticky; top: 48px; z-index: 99; display: flex; gap: 15px; align-items: center; flex-wrap: wrap; }
        .filter-group { display: flex; gap: 10px; align-items: center; }
        .filter-btn { padding: 8px 16px; border: 2px solid #e0e0e0; background: white; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.2s; }
        .filter-btn:hover { border-color: #667eea; background: #f8f9ff; }
        .filter-btn.active { background: #667eea; color: white; border-color: #667eea; }
        .search-box { padding: 8px 12px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 13px; width: 250px; }
        .search-box:focus { outline: none; border-color: #667eea; }
        .summary { display: flex; gap: 15px; padding: 20px 30px; background: #f8f9fa; }
        .summary-card { flex: 1; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }
        .summary-card h3 { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        .summary-card .number { font-size: 28px; font-weight: bold; margin-bottom: 5px; }
        .summary-card.total .number { color: #667eea; }
        .summary-card.passed .number { color: #10b981; }
        .summary-card.failed .number { color: #ef4444; }
        .comparison-list { padding: 20px 30px; max-width: 1600px; margin: 0 auto; }
        .comparison-item { margin-bottom: 15px; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; background: white; transition: all 0.2s; }
        .comparison-item:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .comparison-item.hidden { display: none; }
        .comparison-header { padding: 12px 20px; background: #f8f9fa; cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; }
        .comparison-header:hover { background: #f0f1f3; }
        .comparison-header h3 { font-size: 14px; color: #333; display: flex; align-items: center; gap: 10px; }
        .image-name { cursor: text; user-select: all; padding: 2px 6px; border-radius: 3px; transition: background 0.2s; }
        .image-name:hover { background: #e8e8e8; }
        .expand-icon { font-size: 12px; color: #666; transition: transform 0.2s; }
        .comparison-item.expanded .expand-icon { transform: rotate(90deg); }
        .status { padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .status.pass { background: #d1fae5; color: #065f46; }
        .status.fail { background: #fee2e2; color: #991b1b; }
        .comparison-content { display: none; }
        .comparison-item.expanded .comparison-content { display: block; }
        .details { padding: 12px 20px; background: #fffbeb; border-top: 1px solid #e0e0e0; font-size: 12px; }
        .details-row { display: flex; align-items: center; margin-bottom: 6px; }
        .details-row:last-child { margin-bottom: 0; }
        .details-label { font-weight: 600; margin-right: 8px; min-width: 90px; }
        .check { color: #10b981; margin-right: 5px; }
        .cross { color: #ef4444; margin-right: 5px; }
        .difference { color: #64748b; font-size: 12px; margin-left: 98px; margin-top: 6px; padding: 8px 12px; background: #f8fafc; border-left: 3px solid #94a3b8; border-radius: 3px; line-height: 1.5; }
        .difference.info { color: #475569; background: #f1f5f9; border-left-color: #64748b; }
        .difference.warning { color: #92400e; background: #fef3c7; border-left-color: #f59e0b; }
        .images { display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-top: 1px solid #e0e0e0; }
        .image-container { padding: 15px; background: #fafafa; text-align: center; position: relative; }
        .image-container:first-child { border-right: 1px solid #e0e0e0; }
        .image-label { font-size: 11px; font-weight: 600; color: #666; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
        .image-container img { max-width: 100%; height: auto; border: 1px solid #e0e0e0; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; }
        .image-container img:hover { opacity: 0.85; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); align-items: center; justify-content: center; }
        .modal.active { display: flex; }
        .modal-content { max-width: 95%; max-height: 95%; object-fit: contain; border: 2px solid #fff; border-radius: 4px; }
        .modal-close { position: absolute; top: 20px; right: 40px; color: white; font-size: 40px; font-weight: bold; cursor: pointer; z-index: 1001; background: rgba(0,0,0,0.7); width: 50px; height: 50px; border-radius: 25px; display: flex; align-items: center; justify-content: center; line-height: 1; user-select: none; }
        .modal-close:hover { background: rgba(0,0,0,0.9); }
        .modal-nav { position: absolute; top: 50%; transform: translateY(-50%); color: white; font-size: 48px; font-weight: bold; cursor: pointer; padding: 20px; user-select: none; background: rgba(0,0,0,0.7); border-radius: 4px; z-index: 1001; }
        .modal-nav:hover { background: rgba(0,0,0,0.9); }
        .modal-nav.prev { left: 20px; }
        .modal-nav.next { right: 20px; }
        .modal-info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); color: white; background: rgba(0,0,0,0.8); padding: 15px 25px; border-radius: 4px; font-size: 14px; z-index: 1001; max-width: 80%; text-align: center; }
        .keyboard-hint { font-size: 11px; color: #666; margin-left: auto; }
        .no-results { text-align: center; padding: 60px 20px; color: #666; }
        .no-results-icon { font-size: 48px; margin-bottom: 15px; opacity: 0.5; }
    ''')
    html.append('</style>')
    html.append('</head>')
    html.append('<body>')
    
    # Header
    html.append('<div class="header">')
    html.append('<h1>Image Comparison Report</h1>')
    html.append(f'<p>Comparing images from two versions • {total} total comparisons</p>')
    html.append('</div>')
    
    # Controls
    html.append('<div class="controls">')
    html.append('<div class="filter-group">')
    html.append(f'<button class="filter-btn active" onclick="filterResults(\'all\')">All ({total})</button>')
    html.append(f'<button class="filter-btn" onclick="filterResults(\'pass\')">Passed ({passed})</button>')
    html.append(f'<button class="filter-btn" onclick="filterResults(\'fail\')">Failed ({failed})</button>')
    html.append('</div>')
    html.append('<div class="filter-group">')
    html.append('<button class="filter-btn" onclick="expandAll()">▼ Expand All</button>')
    html.append('<button class="filter-btn" onclick="collapseAll()">▲ Collapse All</button>')
    html.append('</div>')
    html.append('<input type="text" class="search-box" placeholder="Search by image name..." onkeyup="searchImages(this.value)">')
    html.append('<span class="keyboard-hint">Click image to zoom • ↑↓ navigate • ←→ in zoom • ESC close</span>')
    html.append('</div>')
    
    # Summary
    html.append('<div class="summary">')
    html.append('<div class="summary-card total"><h3>Total Compared</h3><div class="number">' + str(total) + '</div></div>')
    html.append('<div class="summary-card passed"><h3>Passed</h3><div class="number">' + str(passed) + '</div></div>')
    html.append('<div class="summary-card failed"><h3>Failed</h3><div class="number">' + str(failed) + '</div></div>')
    html.append('</div>')
    
    # Comparison list
    html.append('<div class="comparison-list" id="comparisonList">')
    
    for idx, result in enumerate(results):
        status_class = "pass" if result.overall_match else "fail"
        status_text = "✓ PASS" if result.overall_match else "✗ FAIL"
        
        text_icon = "✓" if result.text_match else "✗"
        text_class = "check" if result.text_match else "cross"
        focus_icon = "✓" if result.focus_match else "✗"
        focus_class = "check" if result.focus_match else "cross"
        
        # Build differences
        differences_html = ""
        if result.text_differences:
            for diff in result.text_differences:
                # Determine styling class based on message content
                diff_class = "difference"
                if "💡" in diff or "Click images" in diff:
                    diff_class = "difference info"
                elif "⚠️" in diff or "warning" in diff.lower() or "manual review" in diff.lower():
                    diff_class = "difference warning"
                
                differences_html += f'<div class="{diff_class}">{diff}</div>'
        
        if not result.focus_match and 'message' in result.focus_details:
            differences_html += f'<div class="difference info">Focus: {result.focus_details["message"]}</div>'
        
        # Copy images
        img1_src = folder1_path / result.image_name
        img2_src = folder2_path / result.image_name
        
        img1_dest = v1_folder / result.image_name
        img2_dest = v2_folder / result.image_name
        
        shutil.copy2(img1_src, img1_dest)
        shutil.copy2(img2_src, img2_dest)
        
        img1_rel = f"report_images/version1/{result.image_name}"
        img2_rel = f"report_images/version2/{result.image_name}"
        
        html.append(f'<div class="comparison-item" data-status="{status_class}" data-name="{result.image_name.lower()}" data-index="{idx}">')
        html.append(f'<div class="comparison-header" onclick="toggleExpand(this)">')
        html.append(f'<h3><span class="expand-icon">▶</span><span class="image-name">{result.image_name}</span></h3>')
        html.append(f'<span class="status {status_class}">{status_text}</span>')
        html.append('</div>')
        html.append('<div class="comparison-content">')
        html.append('<div class="details">')
        html.append(f'<div class="details-row"><span class="details-label">Text Match:</span><span class="{text_class}">{text_icon}</span><span>{"Match" if result.text_match else "Mismatch"}</span></div>')
        html.append(f'<div class="details-row"><span class="details-label">Focus Match:</span><span class="{focus_class}">{focus_icon}</span><span>{"Match" if result.focus_match else "Mismatch"}</span></div>')
        html.append(differences_html)
        html.append('</div>')
        html.append('<div class="images">')
        html.append(f'<div class="image-container"><div class="image-label">Version 1: {folder1}</div><img src="{img1_rel}" alt="{result.image_name} - Version 1" class="thumbnail-img" data-index="{idx}" data-version="1" onclick="openModal(\'{img1_rel}\', \'{result.image_name}\', \'Version 1\', {idx})"></div>')
        html.append(f'<div class="image-container"><div class="image-label">Version 2: {folder2}</div><img src="{img2_rel}" alt="{result.image_name} - Version 2" class="thumbnail-img" data-index="{idx}" data-version="2" onclick="openModal(\'{img2_rel}\', \'{result.image_name}\', \'Version 2\', {idx})"></div>')
        html.append('</div>')
        html.append('</div>')
        html.append('</div>')
    
    html.append('<div class="no-results" id="noResults" style="display: none;"><div class="no-results-icon">🔍</div><h3>No matching results</h3><p>Try adjusting your filters or search term</p></div>')
    html.append('</div>')
    
    # Modal for zoomed images
    html.append('<div class="modal" id="imageModal" onclick="closeModal(event)">')
    html.append('<span class="modal-close">&times;</span>')
    html.append('<span class="modal-nav prev" onclick="event.stopPropagation(); navigateImage(-1)">‹</span>')
    html.append('<img class="modal-content" id="modalImage">')
    html.append('<span class="modal-nav next" onclick="event.stopPropagation(); navigateImage(1)">›</span>')
    html.append('<div class="modal-info" id="modalInfo"></div>')
    html.append('</div>')
    
    # JavaScript
    html.append('<script>')
    html.append('''
        let currentFilter = 'all';
        let currentSearch = '';
        let currentModalIndex = 0;
        let allItems = [];
        
        document.addEventListener('DOMContentLoaded', function() {
            allItems = Array.from(document.querySelectorAll('.comparison-item'));
        });
        
        function filterResults(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            applyFilters();
        }
        
        function searchImages(query) {
            currentSearch = query.toLowerCase();
            applyFilters();
        }
        
        function applyFilters() {
            let visibleCount = 0;
            allItems.forEach(item => {
                const status = item.dataset.status;
                const name = item.dataset.name;
                const matchesFilter = currentFilter === 'all' || status === currentFilter;
                const matchesSearch = currentSearch === '' || name.includes(currentSearch);
                if (matchesFilter && matchesSearch) {
                    item.classList.remove('hidden');
                    visibleCount++;
                } else {
                    item.classList.add('hidden');
                }
            });
            document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
        }
        
        function toggleExpand(header) {
            const item = header.closest('.comparison-item');
            item.classList.toggle('expanded');
        }
        
        function expandAll() {
            const visibleItems = allItems.filter(item => !item.classList.contains('hidden'));
            visibleItems.forEach(item => {
                item.classList.add('expanded');
            });
        }
        
        function collapseAll() {
            allItems.forEach(item => {
                item.classList.remove('expanded');
            });
        }
        
        function openModal(src, name, version, index) {
            currentModalIndex = index;
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            const modalInfo = document.getElementById('modalInfo');
            modal.classList.add('active');
            modalImg.src = src;
            modalInfo.innerHTML = '<strong>' + name + '</strong><br>' + version;
            document.body.style.overflow = 'hidden';
        }
        
        function closeModal(event) {
            if (event.target.id === 'imageModal' || event.target.className === 'modal-close') {
                const modal = document.getElementById('imageModal');
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        }
        
        function navigateImage(direction) {
            const visibleItems = allItems.filter(item => !item.classList.contains('hidden'));
            const currentItem = visibleItems.find(item => parseInt(item.dataset.index) === currentModalIndex);
            if (!currentItem) return;
            
            const imgs = currentItem.querySelectorAll('.thumbnail-img');
            if (imgs.length === 0) return;
            
            const modalImg = document.getElementById('modalImage');
            const currentSrc = modalImg.src;
            
            // Find current image index by comparing full src URLs
            let currentImgIndex = -1;
            imgs.forEach((img, i) => {
                if (img.src === currentSrc || img.src.endsWith(currentSrc.split('/').slice(-2).join('/'))) {
                    currentImgIndex = i;
                }
            });
            
            // If we couldn't find the current image, default to first image
            if (currentImgIndex === -1) {
                currentImgIndex = 0;
            }
            
            // Calculate next index (wraps around)
            let nextImgIndex = currentImgIndex + direction;
            
            // Handle wrapping
            if (nextImgIndex < 0) {
                nextImgIndex = imgs.length - 1;
            } else if (nextImgIndex >= imgs.length) {
                nextImgIndex = 0;
            }
            
            const nextImg = imgs[nextImgIndex];
            
            if (nextImg) {
                modalImg.src = nextImg.src;
                const version = nextImg.dataset.version === '1' ? 'Version 1' : 'Version 2';
                const name = currentItem.querySelector('h3 .image-name').textContent;
                document.getElementById('modalInfo').innerHTML = '<strong>' + name + '</strong><br>' + version;
            }
        }
        
        document.addEventListener('keydown', function(e) {
            const modal = document.getElementById('imageModal');
            if (modal.classList.contains('active')) {
                if (e.key === 'Escape') {
                    closeModal({ target: modal });
                } else if (e.key === 'ArrowLeft') {
                    navigateImage(-1);
                    e.preventDefault();
                } else if (e.key === 'ArrowRight') {
                    navigateImage(1);
                    e.preventDefault();
                }
            } else {
                const visibleItems = allItems.filter(item => !item.classList.contains('hidden'));
                const expandedItems = visibleItems.filter(item => item.classList.contains('expanded'));
                if (e.key === 'ArrowDown') {
                    if (expandedItems.length > 0) {
                        const currentIndex = visibleItems.indexOf(expandedItems[0]);
                        const nextItem = visibleItems[currentIndex + 1];
                        if (nextItem) {
                            expandedItems[0].classList.remove('expanded');
                            nextItem.classList.add('expanded');
                            nextItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    } else if (visibleItems.length > 0) {
                        visibleItems[0].classList.add('expanded');
                        visibleItems[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    e.preventDefault();
                } else if (e.key === 'ArrowUp') {
                    if (expandedItems.length > 0) {
                        const currentIndex = visibleItems.indexOf(expandedItems[0]);
                        const prevItem = visibleItems[currentIndex - 1];
                        if (prevItem) {
                            expandedItems[0].classList.remove('expanded');
                            prevItem.classList.add('expanded');
                            prevItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }
                    e.preventDefault();
                }
            }
        });
    ''')
    html.append('</script>')
    html.append('</body>')
    html.append('</html>')
    
    # Write file
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f"\nHTML report generated: {output_html}")
    print(f"Images copied to: {images_folder}")
    print(f"\nFeatures:")
    print(f"  ✓ Click image name to select and copy")
    print(f"  ✓ Click image to view zoomed")
    print(f"  ✓ Use ←→ arrows in zoom to switch between Version 1/2")
    print(f"  ✓ Press ESC to close zoom")
    print(f"  ✓ Expand All / Collapse All buttons")
    print(f"  ✓ Click header to show/hide details")
    print(f"  ✓ Filter by Pass/Fail status")
    print(f"  ✓ Search by image name")
    print(f"  ✓ Use ↑↓ arrows to navigate between items")
    return output_html


def compare_folders(folder1: str, folder2: str, output_file: str = None, generate_html: bool = True):
    """Compare all images with matching names in two folders"""
    folder1_path = Path(folder1)
    folder2_path = Path(folder2)
    
    if not folder1_path.exists():
        print(f"Error: Folder '{folder1}' does not exist")
        return
    
    if not folder2_path.exists():
        print(f"Error: Folder '{folder2}' does not exist")
        return
    
    # Get all image files from folder1
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
    images1 = {f.name: f for f in folder1_path.iterdir() 
               if f.suffix.lower() in image_extensions}
    
    if not images1:
        print(f"No images found in {folder1}")
        return
    
    print(f"\nFound {len(images1)} images in {folder1}")
    
    comparator = SmartImageComparator()
    results = []
    
    for img_name, img1_path in images1.items():
        img2_path = folder2_path / img_name
        
        if not img2_path.exists():
            print(f"\nSkipping {img_name} - not found in {folder2}")
            continue
        
        print(f"\n{'='*60}")
        result = comparator.compare_images(str(img1_path), str(img2_path))
        results.append(result)
        
        # Print result
        status = "✓ PASS" if result.overall_match else "✗ FAIL"
        print(f"\n{status}: {result.image_name}")
        print(f"  Text Match: {'✓' if result.text_match else '✗'}")
        if result.text_differences:
            for diff in result.text_differences:
                print(f"    - {diff}")
        print(f"  Focus Match: {'✓' if result.focus_match else '✗'}")
        if not result.focus_match and 'message' in result.focus_details:
            print(f"    - {result.focus_details['message']}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    total = len(results)
    passed = sum(1 for r in results if r.overall_match)
    print(f"Total compared: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    # Generate HTML report
    if generate_html and results:
        generate_html_report(results, folder1, folder2, folder1_path, folder2_path)
    
    # Save results to JSON if requested
    if output_file:
        output_data = []
        for r in results:
            output_data.append({
                'image_name': r.image_name,
                'text_match': r.text_match,
                'text_differences': r.text_differences,
                'focus_match': r.focus_match,
                'focus_details': r.focus_details,
                'overall_match': r.overall_match
            })
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare images focusing on text content and focus elements"
    )
    parser.add_argument("folder1", help="Path to first folder (old version)")
    parser.add_argument("folder2", help="Path to second folder (new version)")
    parser.add_argument("-o", "--output", help="Output JSON file for results")
    
    args = parser.parse_args()
    
    compare_folders(args.folder1, args.folder2, args.output)
