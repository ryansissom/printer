def convert_to_zpl(png_file):
    """Send the PNG to the Labelary API and save the ZPL output."""
    # url = "http://api.labelary.com/v1/graphics"
    # try:
    #     with open(png_file, 'rb') as file:
    #         files = {'file': file}
    #         response = requests.post(url, files=files)

    #     if response.status_code == 200:
    #         zpl_content = response.text
    #         print(f"ZPL Content:\n{zpl_content}")  # Print the ZPL content for debugging
    #         return zpl_content
    #     else:
    #         print("Error:", response.status_code, response.text)
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    # return None