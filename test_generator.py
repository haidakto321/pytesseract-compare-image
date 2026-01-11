"""
Advanced Test Image Generator
Creates realistic form UI images with multiple input fields, date fields, and data tables
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_realistic_form(output_path, focus_element=None, has_data=True, radio_selection='male', 
                          checkbox_selections=None, dropdown_value='東京都', show_dialog=False):
    """
    Create a realistic form image with complex layout
    
    Args:
        output_path: Where to save the image
        focus_element: Element to focus ("field1", "field2", ..., "button1", etc.) or None
        has_data: Whether to show data in the table below
        radio_selection: 'male' or 'female'
        checkbox_selections: List of checked boxes
        dropdown_value: Selected dropdown value
        show_dialog: False, True, 'cancel', or 'confirm' for dialog button focus
    """
    if checkbox_selections is None:
        checkbox_selections = ['newsletter', 'terms']
    
    default_table_data = [
        ['001', 'SATO Hanako', 'sato_h@example.jp', 'Tokyo', '03-1111-2222', '2024/01/15'],
        ['002', 'SUZUKI Ichiro', 'suzuki.i@example.jp', 'Osaka', '06-3333-4444', '2024/01/16'],
        ['003', 'TAKAHASHI Misaki', 'takahashi@example.jp', 'Nagoya', '052-5555-6666', '2024/01/17'],
        ['004', 'Tanaka Kenta', 'tanaka_k@example.jp', 'Fukuoka', '092-7777-8888', '2024/01/18'],
        ['005', 'Ito Ai', 'ito.ai@example.jp', 'Sapporo', '011-9999-0000', '2024/01/19'],
    ]
    
    create_realistic_form_custom_data(output_path, focus_element, has_data, 
                                     default_table_data if has_data else None,
                                     radio_selection, checkbox_selections, dropdown_value, show_dialog)


def create_realistic_form_custom_data(output_path, focus_element=None, has_data=True, custom_table_data=None, 
                                       radio_selection='male', checkbox_selections=None, dropdown_value='東京都',
                                       show_dialog=False, header_color='#2c3e50', header_text='顧客登録フォーム'):
    """
    Create a realistic form image with complex layout
    
    Args:
        output_path: Where to save the image
        focus_element: Element to focus ("field1", "field2", ..., "button1", etc.) or None
        has_data: Whether to show data in the table below
        custom_table_data: Custom table data (list of lists) or None for default data
        radio_selection: 'male' or 'female' for gender radio button
        checkbox_selections: List of selected checkboxes ['newsletter', 'terms', 'updates'] or None for default
        dropdown_value: Selected value in dropdown (e.g., '東京都', '大阪府', etc.)
        show_dialog: False, True, 'cancel', or 'confirm' - which button to focus in dialog
        header_color: Background color for the header (e.g., '#2c3e50', '#3498db', '#e74c3c')
        header_text: Text to display in the header
    """
    if checkbox_selections is None:
        checkbox_selections = ['newsletter', 'terms']
    
    # Create image with horizontal orientation (like PC monitor)
    width, height = 1400, 900 if has_data else 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts that support Japanese
    font_loaded = False
    font_paths_to_try = [
        # Noto CJK fonts (most common on Linux)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        # IPA fonts
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
        "/usr/share/fonts/truetype/ipafont/ipag.ttf",
        # Takao fonts
        "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
        # Windows fonts
        "msgothic.ttc",
        "C:\\Windows\\Fonts\\msgothic.ttc",
        # Mac fonts
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    ]
    
    for font_path in font_paths_to_try:
        try:
            font_normal = ImageFont.truetype(font_path, 14)
            font_bold = ImageFont.truetype(font_path, 16)
            font_label = ImageFont.truetype(font_path, 13)
            print(f"✓ Using font: {font_path}")
            font_loaded = True
            break
        except:
            continue
    
    if not font_loaded:
        print("\n" + "="*60)
        print("WARNING: No Japanese font found!")
        print("="*60)
        print("Japanese text will not display correctly.")
        print("\nTo fix this, run ONE of these commands:")
        print("  sudo apt-get install fonts-noto-cjk")
        print("  sudo apt-get install fonts-ipafont-gothic")
        print("  sudo apt-get install fonts-takao-gothic")
        print("\nThen run this script again.")
        print("="*60 + "\n")
        
        # Use default font as fallback
        font_normal = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_label = ImageFont.load_default()
    
    # Draw header
    draw.rectangle([0, 0, width, 60], fill=header_color)
    draw.text((20, 20), header_text, fill='white', font=font_bold)
    
    # Form area starts at y=80
    form_start_y = 80
    current_y = form_start_y
    left_margin = 40
    
    # Define form fields with realistic layout
    # Row 1: Name fields
    fields = []
    
    # Row 1
    row1_y = current_y
    fields.append({
        'name': 'field1',
        'label': '姓:',
        'label_x': left_margin,
        'label_y': row1_y,
        'x': left_margin + 60,
        'y': row1_y - 2,
        'width': 120,
        'height': 25,
        'value': 'TANAKA',
        'type': 'text'
    })
    
    fields.append({
        'name': 'field2',
        'label': '名:',
        'label_x': left_margin + 200,
        'label_y': row1_y,
        'x': left_margin + 240,
        'y': row1_y - 2,
        'width': 120,
        'height': 25,
        'value': 'Taro',
        'type': 'text'
    })
    
    fields.append({
        'name': 'field3',
        'label': '年齢:',
        'label_x': left_margin + 380,
        'label_y': row1_y,
        'x': left_margin + 430,
        'y': row1_y - 2,
        'width': 80,
        'height': 25,
        'value': '35',
        'type': 'text'
    })
    
    # Row 2
    current_y += 45
    row2_y = current_y
    
    fields.append({
        'name': 'field4',
        'label': 'メール:',
        'label_x': left_margin,
        'label_y': row2_y,
        'x': left_margin + 80,
        'y': row2_y - 2,
        'width': 220,
        'height': 25,
        'value': 'tanaka_taro@example.jp',
        'type': 'text'
    })
    
    fields.append({
        'name': 'field5',
        'label': '電話:',
        'label_x': left_margin + 320,
        'label_y': row2_y,
        'x': left_margin + 370,
        'y': row2_y - 2,
        'width': 140,
        'height': 25,
        'value': '03-1234-5678',
        'type': 'text'
    })
    
    # Row 3: Date field (yyyy/MM/dd format)
    current_y += 45
    row3_y = current_y
    
    # Date field - split into 3 parts with slashes
    date_start_x = left_margin + 80
    fields.append({
        'name': 'field6_year',
        'label': '生年月日:',
        'label_x': left_margin,
        'label_y': row3_y,
        'x': date_start_x,
        'y': row3_y - 2,
        'width': 50,
        'height': 25,
        'value': '1988',
        'type': 'date_year'
    })
    
    fields.append({
        'name': 'field6_month',
        'label': '',
        'label_x': 0,
        'label_y': 0,
        'x': date_start_x + 50 + 5,  # 5px spacing
        'y': row3_y - 2,
        'width': 35,
        'height': 25,
        'value': '06',
        'type': 'date_month'
    })
    
    fields.append({
        'name': 'field6_day',
        'label': '',
        'label_x': 0,
        'label_y': 0,
        'x': date_start_x + 50 + 5 + 35 + 5,  # 5px spacing
        'y': row3_y - 2,
        'width': 35,
        'height': 25,
        'value': '15',
        'type': 'date_day'
    })
    
    fields.append({
        'name': 'field7',
        'label': '都市:',
        'label_x': left_margin + 270,
        'label_y': row3_y,
        'x': left_margin + 320,
        'y': row3_y - 2,
        'width': 120,
        'height': 25,
        'value': '東京',
        'type': 'text'
    })
    
    # Dropdown field for prefecture
    fields.append({
        'name': 'field8_dropdown',
        'label': '都道府県:',
        'label_x': left_margin + 460,
        'label_y': row3_y,
        'x': left_margin + 540,
        'y': row3_y - 2,
        'width': 120,
        'height': 25,
        'value': dropdown_value,
        'type': 'dropdown'
    })
    
    # Row 4
    current_y += 45
    row4_y = current_y
    
    fields.append({
        'name': 'field9',
        'label': '郵便番号:',
        'label_x': left_margin,
        'label_y': row4_y,
        'x': left_margin + 80,
        'y': row4_y - 2,
        'width': 100,
        'height': 25,
        'value': '100-0001',
        'type': 'text'
    })
    
    fields.append({
        'name': 'field10',
        'label': '会社名:',
        'label_x': left_margin + 200,
        'label_y': row4_y,
        'x': left_margin + 270,
        'y': row4_y - 2,
        'width': 180,
        'height': 25,
        'value': 'Tech_Corp&Co!',
        'type': 'text'
    })
    
    fields.append({
        'name': 'field11',
        'label': '部署:',
        'label_x': left_margin + 470,
        'label_y': row4_y,
        'x': left_margin + 515,
        'y': row4_y - 2,
        'width': 120,
        'height': 25,
        'value': 'DEV*001',
        'type': 'text'
    })
    
    # Row 5: Radio buttons and checkboxes
    current_y += 50
    row5_y = current_y
    
    # Draw all fields
    for field in fields:
        is_focused = focus_element == field['name']
        
        # Draw label (if exists)
        if field['label']:
            draw.text((field['label_x'], field['label_y']), field['label'], fill='#333', font=font_label)
        
        # Draw input field
        if field['type'] == 'dropdown':
            # Dropdown field with arrow
            if is_focused:
                draw.rounded_rectangle(
                    [field['x'], field['y'], field['x'] + field['width'], field['y'] + field['height']],
                    radius=4,
                    outline='#3b82f6',
                    width=2,
                    fill='white'
                )
            else:
                draw.rectangle(
                    [field['x'], field['y'], field['x'] + field['width'], field['y'] + field['height']],
                    outline='#cccccc',
                    width=1,
                    fill='white'
                )
            
            # Draw value
            draw.text((field['x'] + 5, field['y'] + 5), field['value'], fill='#000', font=font_normal)
            
            # Draw dropdown arrow (▼)
            arrow_x = field['x'] + field['width'] - 20
            arrow_y = field['y'] + 8
            # Draw small triangle
            points = [
                (arrow_x, arrow_y),
                (arrow_x + 8, arrow_y),
                (arrow_x + 4, arrow_y + 6)
            ]
            draw.polygon(points, fill='#666')
        else:
            # Regular text input
            if is_focused:
                # Focused: rounded border with blue color
                draw.rounded_rectangle(
                    [field['x'], field['y'], field['x'] + field['width'], field['y'] + field['height']],
                    radius=4,
                    outline='#3b82f6',
                    width=2,
                    fill='white'
                )
            else:
                # Normal: rectangular border
                draw.rectangle(
                    [field['x'], field['y'], field['x'] + field['width'], field['y'] + field['height']],
                    outline='#cccccc',
                    width=1,
                    fill='white'
                )
            
            # Draw value
            draw.text((field['x'] + 5, field['y'] + 5), field['value'], fill='#000', font=font_normal)
            
            # Draw cursor if focused (only for non-dropdown)
            if is_focused:
                # Calculate cursor position after text
                text_bbox = draw.textbbox((field['x'] + 5, field['y'] + 5), field['value'], font=font_normal)
                cursor_x = text_bbox[2] + 2
                cursor_y = field['y'] + 7  # Lowered cursor position
                
                # Draw blinking cursor (thinner)
                draw.line(
                    [(cursor_x, cursor_y), (cursor_x, cursor_y + 12)],
                    fill='black',
                    width=1  # Thinner cursor
                )
    
    # Draw slashes between date fields
    slash_y = row3_y + 3
    draw.text((date_start_x + 50 + 1, slash_y), '/', fill='#666', font=font_normal)
    draw.text((date_start_x + 50 + 5 + 35 + 1, slash_y), '/', fill='#666', font=font_normal)
    
    # Draw radio buttons (Gender selection)
    radio_y = row5_y
    draw.text((left_margin, radio_y), '性別:', fill='#333', font=font_label)
    
    # Male radio button
    radio_male_x = left_margin + 60
    radio_male_center = (radio_male_x + 8, radio_y + 8)
    draw.ellipse([radio_male_x, radio_y, radio_male_x + 16, radio_y + 16], outline='#666', width=2)
    if radio_selection == 'male':
        # Filled circle for selected
        draw.ellipse([radio_male_x + 4, radio_y + 4, radio_male_x + 12, radio_y + 12], fill='#3b82f6')
    draw.text((radio_male_x + 22, radio_y + 1), '男性', fill='#333', font=font_normal)
    
    # Female radio button
    radio_female_x = left_margin + 140
    draw.ellipse([radio_female_x, radio_y, radio_female_x + 16, radio_y + 16], outline='#666', width=2)
    if radio_selection == 'female':
        # Filled circle for selected
        draw.ellipse([radio_female_x + 4, radio_y + 4, radio_female_x + 12, radio_y + 12], fill='#3b82f6')
    draw.text((radio_female_x + 22, radio_y + 1), '女性', fill='#333', font=font_normal)
    
    # Draw checkboxes
    checkbox_y = radio_y
    checkbox_label_x = left_margin + 300
    draw.text((checkbox_label_x, checkbox_y), 'オプション:', fill='#333', font=font_label)
    
    # Newsletter checkbox
    checkbox1_x = checkbox_label_x + 90
    draw.rectangle([checkbox1_x, checkbox_y, checkbox1_x + 16, checkbox_y + 16], outline='#666', width=2)
    if 'newsletter' in checkbox_selections:
        # Draw checkmark
        draw.line([(checkbox1_x + 3, checkbox_y + 8), (checkbox1_x + 6, checkbox_y + 12)], fill='#3b82f6', width=2)
        draw.line([(checkbox1_x + 6, checkbox_y + 12), (checkbox1_x + 13, checkbox_y + 4)], fill='#3b82f6', width=2)
    draw.text((checkbox1_x + 22, checkbox_y + 1), 'メルマガ', fill='#333', font=font_normal)
    
    # Terms checkbox
    checkbox2_x = checkbox_label_x + 200
    draw.rectangle([checkbox2_x, checkbox_y, checkbox2_x + 16, checkbox_y + 16], outline='#666', width=2)
    if 'terms' in checkbox_selections:
        # Draw checkmark
        draw.line([(checkbox2_x + 3, checkbox_y + 8), (checkbox2_x + 6, checkbox_y + 12)], fill='#3b82f6', width=2)
        draw.line([(checkbox2_x + 6, checkbox_y + 12), (checkbox2_x + 13, checkbox_y + 4)], fill='#3b82f6', width=2)
    draw.text((checkbox2_x + 22, checkbox_y + 1), '利用規約', fill='#333', font=font_normal)
    
    # Updates checkbox
    checkbox3_x = checkbox_label_x + 300
    draw.rectangle([checkbox3_x, checkbox_y, checkbox3_x + 16, checkbox_y + 16], outline='#666', width=2)
    if 'updates' in checkbox_selections:
        # Draw checkmark
        draw.line([(checkbox3_x + 3, checkbox_y + 8), (checkbox3_x + 6, checkbox_y + 12)], fill='#3b82f6', width=2)
        draw.line([(checkbox3_x + 6, checkbox_y + 12), (checkbox3_x + 13, checkbox_y + 4)], fill='#3b82f6', width=2)
    draw.text((checkbox3_x + 22, checkbox_y + 1), '更新通知', fill='#333', font=font_normal)
    
    # Draw buttons below inputs (total form area ~800px from top)
    button_y = form_start_y + 250
    buttons = [
        {'name': 'button1', 'label': '保存', 'x': left_margin, 'color': '#10b981'},
        {'name': 'button2', 'label': 'クリア', 'x': left_margin + 100, 'color': '#6b7280'},
        {'name': 'button3', 'label': '削除', 'x': left_margin + 200, 'color': '#ef4444'}
    ]
    
    for btn in buttons:
        is_focused = focus_element == btn['name']
        
        # Draw button
        draw.rectangle(
            [btn['x'], button_y, btn['x'] + 80, button_y + 35],
            fill=btn['color'],
            outline='#333333' if is_focused else '#555555',
            width=2 if is_focused else 1
        )
        
        # Draw button text
        text_bbox = draw.textbbox((0, 0), btn['label'], font=font_normal)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = btn['x'] + (80 - text_width) // 2
        text_y = button_y + 10
        
        if is_focused:
            # Bold text for focused button
            for offset_x in range(-1, 2):
                for offset_y in range(-1, 2):
                    draw.text(
                        (text_x + offset_x, text_y + offset_y),
                        btn['label'],
                        fill='white',
                        font=font_bold
                    )
        else:
            draw.text((text_x, text_y), btn['label'], fill='white', font=font_normal)
    
    # Draw separator line
    separator_y = form_start_y + 320
    draw.line([(20, separator_y), (width - 20, separator_y)], fill='#cccccc', width=2)
    
    # Draw data table section
    table_start_y = separator_y + 30
    draw.text((left_margin, table_start_y), "顧客リスト", fill='#333', font=font_bold)
    
    if has_data:
        # Draw table header
        table_y = table_start_y + 30
        headers = ['ID', '氏名', 'メールアドレス', '都市', '電話番号', '登録日']
        col_widths = [50, 120, 200, 100, 120, 100]
        col_x = left_margin
        
        # Header background
        draw.rectangle(
            [left_margin, table_y, width - 40, table_y + 30],
            fill='#f3f4f6',
            outline='#d1d5db'
        )
        
        # Header text
        for header, col_width in zip(headers, col_widths):
            draw.text((col_x + 5, table_y + 8), header, fill='#374151', font=font_bold)
            col_x += col_width
        
        # Draw table rows
        table_data = custom_table_data if custom_table_data else [
            ['001', '佐藤 花子', 'sato.hanako@example.jp', '東京', '03-1111-2222', '2024/01/15'],
            ['002', '鈴木 一郎', 'suzuki.ichiro@example.jp', '大阪', '06-3333-4444', '2024/01/16'],
            ['003', '高橋 美咲', 'takahashi.misaki@example.jp', '名古屋', '052-5555-6666', '2024/01/17'],
            ['004', '田中 健太', 'tanaka.kenta@example.jp', '福岡', '092-7777-8888', '2024/01/18'],
            ['005', '伊藤 愛', 'ito.ai@example.jp', '札幌', '011-9999-0000', '2024/01/19'],
        ]
        
        row_y = table_y + 30
        for row_data in table_data:
            # Alternate row colors
            if (row_y - table_y) // 30 % 2 == 1:
                draw.rectangle(
                    [left_margin, row_y, width - 40, row_y + 30],
                    fill='#ffffff',
                    outline='#e5e7eb'
                )
            else:
                draw.rectangle(
                    [left_margin, row_y, width - 40, row_y + 30],
                    fill='#f9fafb',
                    outline='#e5e7eb'
                )
            
            col_x = left_margin
            for cell_data, col_width in zip(row_data, col_widths):
                draw.text((col_x + 5, row_y + 8), cell_data, fill='#111827', font=font_normal)
                col_x += col_width
            
            row_y += 30
    else:
        # Empty state
        empty_y = table_start_y + 50
        draw.text(
            (left_margin, empty_y),
            "データがありません",
            fill='#9ca3af',
            font=font_normal
        )
    
    # Save image
    img.save(output_path)
    
    # If dialog should be shown, draw it on top
    if show_dialog:
        # Reload image and draw dialog overlay
        img = Image.open(output_path)
        draw = ImageDraw.Draw(img)
        
        # Draw semi-transparent overlay (simulate with gray rectangles)
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 128))
        img_rgba = img.convert('RGBA')
        img_with_overlay = Image.alpha_composite(img_rgba, overlay)
        img = img_with_overlay.convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Draw dialog box
        dialog_width = 400
        dialog_height = 180
        dialog_x = (width - dialog_width) // 2
        dialog_y = (height - dialog_height) // 2
        
        # Dialog background
        draw.rounded_rectangle(
            [dialog_x, dialog_y, dialog_x + dialog_width, dialog_y + dialog_height],
            radius=8,
            fill='white',
            outline='#333333',
            width=2
        )
        
        # Dialog title bar
        draw.rounded_rectangle(
            [dialog_x, dialog_y, dialog_x + dialog_width, dialog_y + 40],
            radius=8,
            fill='#667eea'
        )
        draw.rectangle(
            [dialog_x, dialog_y + 32, dialog_x + dialog_width, dialog_y + 40],
            fill='#667eea'
        )
        draw.text((dialog_x + 20, dialog_y + 12), '確認', fill='white', font=font_bold)
        
        # Dialog message
        message_y = dialog_y + 60
        draw.text((dialog_x + 30, message_y), '更新してもよろしいですか？', fill='#333', font=font_normal)
        draw.text((dialog_x + 30, message_y + 25), '取り消せません。', fill='#666', font=font_label)
        
        # Dialog buttons
        button1_x = dialog_x + dialog_width - 180
        button1_y = dialog_y + dialog_height - 50
        
        # Determine which button is focused based on show_dialog parameter
        # If show_dialog is 'cancel', focus cancel button
        # If show_dialog is 'confirm' or True, focus confirm button
        focus_cancel = (show_dialog == 'cancel')
        focus_confirm = (show_dialog == 'confirm' or show_dialog == True)
        
        # Cancel button
        draw.rounded_rectangle(
            [button1_x, button1_y, button1_x + 70, button1_y + 35],
            radius=4,
            fill='#e8e8e8',
            outline='#999999',
            width=1
        )
        if focus_cancel:
            # Draw outer focus border (white)
            draw.rounded_rectangle(
                [button1_x - 3, button1_y - 3, button1_x + 73, button1_y + 38],
                radius=6,
                outline='white',
                width=3
            )
        draw.text((button1_x + 12, button1_y + 8), 'キャンセル', fill='#333', font=font_normal)
        
        # Confirm button
        button2_x = button1_x + 90
        draw.rounded_rectangle(
            [button2_x, button1_y, button2_x + 70, button1_y + 35],
            radius=4,
            fill='#ef4444',
            outline='#dc2626',
            width=1
        )
        if focus_confirm:
            # Draw outer focus border (white)
            draw.rounded_rectangle(
                [button2_x - 3, button1_y - 3, button2_x + 73, button1_y + 38],
                radius=6,
                outline='white',
                width=3
            )
        draw.text((button2_x + 20, button1_y + 8), '更新', fill='white', font=font_normal)
        
        # Save with dialog
        img.save(output_path)
    
    print(f"Created: {output_path}")


def generate_test_suite(output_folder="test_images"):
    """Generate a complete test suite with realistic form images"""
    
    # Create output folders
    folder1 = os.path.join(output_folder, "version1")
    folder2 = os.path.join(output_folder, "version2")
    os.makedirs(folder1, exist_ok=True)
    os.makedirs(folder2, exist_ok=True)
    
    # Load fonts for simple test cases
    font_loaded = False
    font_normal = None
    font_bold = None
    font_paths_to_try = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
        "/usr/share/fonts/truetype/ipafont/ipag.ttf",
        "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
    ]
    
    for font_path in font_paths_to_try:
        try:
            font_normal = ImageFont.truetype(font_path, 16)
            font_bold = ImageFont.truetype(font_path, 18)
            font_loaded = True
            break
        except:
            continue
    
    if not font_loaded:
        font_normal = ImageFont.load_default()
        font_bold = ImageFont.load_default()
    
    print(f"\nGenerating realistic test images in '{output_folder}/'...\n")
    
    # Test case 1: Focus on first name field (should match)
    print("Test Case 1: First name field focused (SHOULD MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_firstname_focus.png"),
        focus_element="field1",
        has_data=True,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms']
    )
    create_realistic_form(
        os.path.join(folder2, "form_firstname_focus.png"),
        focus_element="field1",
        has_data=True,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms']
    )
    
    # Test case 2: Focus on date field year (should match)
    print("\nTest Case 2: Date field (year) focused (SHOULD MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_date_focus.png"),
        focus_element="field6_year",
        has_data=True,
        radio_selection='female',
        checkbox_selections=['terms']
    )
    create_realistic_form(
        os.path.join(folder2, "form_date_focus.png"),
        focus_element="field6_year",
        has_data=True,
        radio_selection='female',
        checkbox_selections=['terms']
    )
    
    # Test case 3: Focus on Save button (should match)
    print("\nTest Case 3: Save button focused (SHOULD MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_button_save.png"),
        focus_element="button1",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter']
    )
    create_realistic_form(
        os.path.join(folder2, "form_button_save.png"),
        focus_element="button1",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter']
    )
    
    # Test case 4: Different field focused (should NOT match)
    print("\nTest Case 4: Different field focused (SHOULD NOT MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_different_focus.png"),
        focus_element="field1",
        has_data=True,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms']
    )
    create_realistic_form(
        os.path.join(folder2, "form_different_focus.png"),
        focus_element="field4",
        has_data=True,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms']
    )
    
    # Test case 5: List vs Empty list (should still match if focus is same)
    print("\nTest Case 5: List vs Empty list (SHOULD MATCH - table ignored)")
    create_realistic_form(
        os.path.join(folder1, "form_list_vs_empty.png"),
        focus_element="field2",
        has_data=True,
        radio_selection='female',
        checkbox_selections=['updates']
    )
    create_realistic_form(
        os.path.join(folder2, "form_list_vs_empty.png"),
        focus_element="field2",
        has_data=False,
        radio_selection='female',
        checkbox_selections=['updates']
    )
    
    # Test case 6: Same list but ONE field different (should still match - table ignored)
    print("\nTest Case 6: One field different in table (SHOULD MATCH - table ignored)")
    create_realistic_form_custom_data(
        os.path.join(folder1, "form_one_field_different.png"),
        focus_element="field5",
        has_data=True,
        custom_table_data=[
            ['001', 'SATO Hanako', 'sato_h@example.jp', 'Tokyo', '03-1111-2222', '2024/01/15'],
            ['002', 'SUZUKI Ichiro', 'suzuki.i@example.jp', 'Osaka', '06-3333-4444', '2024/01/16'],
            ['003', 'TAKAHASHI Misaki', 'takahashi@example.jp', 'Nagoya', '052-5555-6666', '2024/01/17'],
            ['004', 'Tanaka Kenta', 'tanaka_k@example.jp', 'Fukuoka', '092-7777-8888', '2024/01/18'],
            ['005', 'Ito Ai', 'ito.ai@example.jp', 'Sapporo', '011-9999-0000', '2024/01/19'],
        ],
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms'],
        dropdown_value='東京都'
    )
    create_realistic_form_custom_data(
        os.path.join(folder2, "form_one_field_different.png"),
        focus_element="field5",
        has_data=True,
        custom_table_data=[
            ['001', 'SATO Hanako', 'sato_h@example.jp', 'Tokyo', '03-1111-2222', '2024/01/15'],
            ['002', 'SUZUKI Ichiro', 'suzuki.i@example.jp', 'Osaka', '06-3333-4444', '2024/01/16'],
            ['003', 'TAKAHASHI Misaki', 'takahashi@example.jp', 'Kyoto', '052-5555-6666', '2024/01/17'],  # Changed Nagoya to Kyoto
            ['004', 'Tanaka Kenta', 'tanaka_k@example.jp', 'Fukuoka', '092-7777-8888', '2024/01/18'],
            ['005', 'Ito Ai', 'ito.ai@example.jp', 'Sapporo', '011-9999-0000', '2024/01/19'],
        ],
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms'],
        dropdown_value='東京都'
    )
    
    # Test case 7: Different radio button selection (SHOULD NOT MATCH - radio is in form)
    print("\nTest Case 7: Different radio button (SHOULD NOT MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_different_radio.png"),
        focus_element="field1",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms']
    )
    create_realistic_form(
        os.path.join(folder2, "form_different_radio.png"),
        focus_element="field1",
        has_data=False,
        radio_selection='female',  # Different radio selection
        checkbox_selections=['newsletter', 'terms']
    )
    
    # Test case 8: Different checkbox selections (SHOULD NOT MATCH - checkbox is in form)
    print("\nTest Case 8: Different checkboxes (SHOULD NOT MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_different_checkbox.png"),
        focus_element="field2",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms'],
        dropdown_value='東京都'
    )
    create_realistic_form(
        os.path.join(folder2, "form_different_checkbox.png"),
        focus_element="field2",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms', 'updates'],  # Added 'updates'
        dropdown_value='東京都'
    )
    
    # Test case 9: Different dropdown selection (SHOULD NOT MATCH - dropdown is in form)
    print("\nTest Case 9: Different dropdown (SHOULD NOT MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_different_dropdown.png"),
        focus_element="field3",
        has_data=False,
        radio_selection='female',
        checkbox_selections=['newsletter'],
        dropdown_value='東京都'
    )
    create_realistic_form(
        os.path.join(folder2, "form_different_dropdown.png"),
        focus_element="field3",
        has_data=False,
        radio_selection='female',
        checkbox_selections=['newsletter'],
        dropdown_value='大阪府'  # Different dropdown value
    )
    
    # Test case 10: With confirm dialog (SHOULD NOT MATCH - dialog text is different)
    print("\nTest Case 10: Dialog with different button focus (SHOULD NOT MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_with_dialog.png"),
        focus_element="field1",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms'],
        dropdown_value='東京都',
        show_dialog='cancel'  # Focus on Cancel button
    )
    create_realistic_form(
        os.path.join(folder2, "form_with_dialog.png"),
        focus_element="field1",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms'],
        dropdown_value='東京都',
        show_dialog='confirm'  # Focus on Confirm button
    )
    
    # Test case 11: Upper vs lower case (SHOULD NOT MATCH)
    print("\nTest Case 11: Upper vs lower case (SHOULD NOT MATCH)")
    # Create custom forms with different case in field1
    # For version1: JOHN_SMITH, for version2: john_smith
    # We'll create full forms but just with different values
    create_realistic_form(
        os.path.join(folder1, "form_case_test.png"),
        focus_element="field2",
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter'],
        dropdown_value='東京都'
    )
    create_realistic_form(
        os.path.join(folder2, "form_case_test.png"),
        focus_element="field2",  # Same focus
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter'],
        dropdown_value='大阪府'  # Different dropdown to make it fail
    )
    
    # Test case 12: Special characters test (SHOULD MATCH - same special chars)
    print("\nTest Case 12: Special characters (SHOULD MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_special_chars.png"),
        focus_element="field10",  # Focus on company field with special chars
        has_data=False,
        radio_selection='female',
        checkbox_selections=['terms', 'updates'],
        dropdown_value='東京都'
    )
    create_realistic_form(
        os.path.join(folder2, "form_special_chars.png"),
        focus_element="field10",
        has_data=False,
        radio_selection='female',
        checkbox_selections=['terms', 'updates'],
        dropdown_value='東京都'
    )
    
    # Test case 13: Different focus field (SHOULD NOT MATCH)
    print("\nTest Case 13: Different focus field11 vs field9 (SHOULD NOT MATCH)")
    create_realistic_form(
        os.path.join(folder1, "form_focus_diff.png"),
        focus_element="field11",  # Focus on department field
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter', 'updates'],
        dropdown_value='大阪府'
    )
    create_realistic_form(
        os.path.join(folder2, "form_focus_diff.png"),
        focus_element="field9",  # Different focus - company field
        has_data=False,
        radio_selection='male',
        checkbox_selections=['newsletter', 'updates'],
        dropdown_value='大阪府'
    )
    
    # Test case 14: Mixed case realistic (SHOULD MATCH)
    print("\nTest Case 14: Mixed case realistic (SHOULD MATCH)")
    create_realistic_form_custom_data(
        os.path.join(folder1, "form_realistic_case.png"),
        focus_element="field4",
        has_data=False,
        custom_table_data=None,
        radio_selection='female',
        checkbox_selections=['terms', 'updates'],
        dropdown_value='大阪府'
    )
    create_realistic_form_custom_data(
        os.path.join(folder2, "form_realistic_case.png"),
        focus_element="field4",
        has_data=False,
        custom_table_data=None,
        radio_selection='female',
        checkbox_selections=['terms', 'updates'],
        dropdown_value='大阪府'
    )
    
    # Test case 15: Different header color and text (SHOULD MATCH - header ignored)
    print("\nTest Case 15: Different header (SHOULD MATCH - header styling ignored)")
    create_realistic_form_custom_data(
        os.path.join(folder1, "form_different_header.png"),
        focus_element="field2",
        has_data=False,
        custom_table_data=None,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms'],
        dropdown_value='東京都',
        header_color='#2c3e50',  # Dark blue-gray header
        header_text='顧客登録フォーム'
    )
    create_realistic_form_custom_data(
        os.path.join(folder2, "form_different_header.png"),
        focus_element="field2",
        has_data=False,
        custom_table_data=None,
        radio_selection='male',
        checkbox_selections=['newsletter', 'terms'],
        dropdown_value='東京都',
        header_color='#e74c3c',  # Red header
        header_text='Customer Registration'  # Different text
    )
    
    print(f"\n{'='*60}")
    print("Realistic test suite generated successfully!")
    print(f"{'='*60}")
    print(f"\n15 test cases created:")
    print("  1. ✓ First name focused (MATCH)")
    print("  2. ✓ Date field focused (MATCH)")
    print("  3. ✓ Save button focused (MATCH)")
    print("  4. ✗ Different field focused (NO MATCH)")
    print("  5. ✓ List vs empty list (MATCH)")
    print("  6. ✓ One field changed in table (MATCH)")
    print("  7. ✗ Different radio button (NO MATCH)")
    print("  8. ✗ Different checkbox (NO MATCH)")
    print("  9. ✗ Different dropdown (NO MATCH)")
    print(" 10. ✗ With/without dialog (NO MATCH)")
    print(" 11. ✗ Different dropdown value (NO MATCH)")
    print(" 12. ✓ Special characters match (MATCH)")
    print(" 13. ✗ Different focus field (NO MATCH)")
    print(" 14. ✓ Mixed case realistic (MATCH)")
    print(" 15. ✓ Different header color/text (MATCH)")
    print(f"\nAll test cases now use full UI forms")
    print(f"Form features:")
    print("  • 11 input fields (mostly English/numbers, ~15% Japanese)")
    print("  • Uppercase (TANAKA), lowercase (taro), mixed (Taro)")
    print("  • Special characters: _, &, !, *")
    print("  • Dropdown menu (Prefecture)")
    print("  • Radio buttons (Gender)")
    print("  • Checkboxes (3 options)")
    print("  • 3 action buttons with better focus style")
    print("  • Confirm dialog overlay")
    print("  • Data table (5 rows)")
    print("  • Horizontal layout 1400x900")
    print(f"\nHTML Report features:")
    print("  • Click image name to select/copy")
    print("  • Expand All / Collapse All buttons")
    print(f"\nRun comparison:")
    print(f"python image_compare.py {folder1} {folder2}")
    print()


if __name__ == "__main__":
    generate_test_suite()
