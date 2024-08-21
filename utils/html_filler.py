def load_html_template(template_path, num_days, best_stocks_html, worst_stocks_html):
    # Ensure proper reading of the file with correct encoding
    with open(template_path, 'r', encoding='utf-8') as file:
        template = file.read()
    
    # Replace placeholders with actual values
    filled_html = template.replace("{{ num_days }}", str(num_days))
    filled_html = filled_html.replace("{{ best_stocks_html }}", best_stocks_html)
    filled_html = filled_html.replace("{{ worst_stocks_html }}", worst_stocks_html)
    
    return filled_html