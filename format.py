def json_to_custom_format(json_obj, kpi_objects):
    custom_format = {
        "type": "doc",
        "content": []
    }
    
    # Title
    custom_format["content"].append({
        "type": "heading",
        "attrs": {"level": 2},
        "content": [{"type": "text", "text": json_obj['Title']['Content']}]
    })
    
    # Sections
    sections = ['Introduction', 'Methods', 'Results', 'Discussion']
    for section in sections:
        custom_format["content"].append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": section}]
        })
        custom_format["content"].append({
            "type": "paragraph",
            "content": [{"type": "text", "text": json_obj[section]['Content']}]
        })
    
    # KPI Objects
    for kpi_key, kpi_data in kpi_objects.items():
        # Add image
        custom_format["content"].append({
            "type": "image",
            "attrs": {"src": kpi_data['image_path']}
        })
        # Add description as subheading
        custom_format["content"].append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": kpi_data['description']}]
        })
        # Add caption as text
        custom_format["content"].append({
            "type": "paragraph",
            "content": [{"type": "text", "text": kpi_data['caption']}]
        })

    return custom_format