def read_sales_data(filename):
    """
    Reads sales data from file and handles encoding issues.
    Returns: list of raw lines (strings)
    """
    # The assignment asks us to try these specific encodings
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    # We try each encoding one by one until one works
    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as file:
                # 1. Read all lines from the file
                lines = file.readlines()
                
                # 2. Skip the header row (lines[1:])
                # 3. Use strip() to remove the '\n' at the end of lines
                # 4. 'if line.strip()' ensures we skip empty lines
                raw_lines = [line.strip() for line in lines[1:] if line.strip()]
                
                print(f"Successfully loaded data using {enc} encoding.")
                return raw_lines
                
        except UnicodeDecodeError:
            # If 'utf-8' fails, it will jump here and try 'latin-1' next
            continue
        except FileNotFoundError:
            # If the file isn't in the folder, we print a nice error
            print(f"Error: The file at {filename} was not found.")
            return []

    return []