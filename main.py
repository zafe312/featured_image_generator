import streamlit as st
from PIL import Image
import numpy as np
from PIL import ImageFont
from PIL import ImageDraw
from datetime import datetime
import os
import zipfile
import requests
from io import BytesIO
import csv

from io import BytesIO
buf = BytesIO()

st.header("Featured image generator",divider='rainbow')
st.subheader("Follow these steps")

st.markdown(
    """
    - Step 1: Input company name, job title in the given format in the text box.
    - Step 2: Click "Generate" button to generate the featured images.
    - Step 3: Click "Download ZIP" button to download Zip file containing the images.
    """
)


date_today = datetime.today().strftime('%Y-%m-%d')
data_str = st.text_area("Job details",value='Apple,Software Developer,\nGoogle, Human Resource Manager')
data_str = data_str.strip()
if data_str[-1]==',':
    data_str = data_str[:-1]
data_str = data_str.replace('\n','')
data_list = np.array(data_str.split(","))
try:
    data_list = np.reshape(data_list,(int(data_list.shape[0]/2),2))
except:
    st.markdown("Some commas are missing. Put the commas and press Ctrl+Enter.")
# st.markdown(data_list[:,0])


company_names = [data_list[i,0].strip() for i in range(data_list.shape[0])]
job_positions = [data_list[i,1].strip() for i in range(data_list.shape[0])]

company_logos = {}

with open(os.path.join(os.getcwd(),f'data/company_logo.csv')) as f:
    next(f)  # Skip the header
    reader = csv.reader(f, skipinitialspace=True)
    company_logos = dict(reader)

button_clicked = st.button("Generate images")

generated_image_names = []

if os.path.isfile(os.path.join(os.getcwd(),f'generated_images/{date_today}_images.zip')):
    os.remove(os.path.join(os.getcwd(),f'generated_images/{date_today}_images.zip'))

if button_clicked:

    for i, company_name in enumerate(company_names):

        company_name = company_name.lower()
        
        template_number = np.random.choice([1,2,3])

        img1 = Image.open(os.path.join(os.getcwd(),f'featured_image_templates/featured_image_template_{template_number}.png'))
        try:
            # img2 = Image.open(os.path.join(os.getcwd(),f'company_logos/{company_name}_logo.png'))
            url = company_logos[company_name]
            response = requests.get(url)
            img2 = Image.open(BytesIO(response.content))
        except:
            st.markdown(f'No logo found for {company_name.capitalize()} in database. Check spelling or upload logo.')
            continue

        # # No transparency mask specified,  
        # # simulating an raster overlay
        base_height = 200
        hpercent = (base_height / float(img2.size[1]))
        wsize = int((float(img2.size[0]) * float(hpercent)))

        base_width = 450
        wpercent = (base_width / float(img2.size[0]))
        hsize = int((float(img2.size[1]) * float(wpercent)))
        if wsize<450:
            img2 = img2.resize((wsize, base_height), Image.Resampling.LANCZOS)
        else:
            img2 = img2.resize((base_width, hsize), Image.Resampling.LANCZOS)

        img1.paste(img2, (315-int(img2.size[0]/2),250-int(img2.size[1]/2)))

        draw = ImageDraw.Draw(img1)
        font = ImageFont.truetype(os.path.join(os.getcwd(),f"fonts/Arial.ttf"), 46)
        draw.text((100, 400),job_positions[i],(255,255,255),font=font)
        # draw.text((50, 200),job_positions[i],(255,25,255),font=font)
        
        image_name = f'{date_today}_{company_name}'
        while image_name + '.png' in generated_image_names:
            image_name += f'_{np.random.randint(1,100)}'
        image_path = os.path.join(os.getcwd(),f'generated_images/{image_name}.png')
        img1.save(image_path)
        generated_image_names.append(image_name+'.png')

    # st.markdown(f"Images generated")

    with zipfile.ZipFile(os.path.join(os.getcwd(),f'generated_images/{date_today}_images.zip'), 'w') as img_zip:
        for image_name in generated_image_names:
            img_name = image_name
            img_data = os.path.join(os.getcwd(),f'generated_images/{image_name}')
            img_zip.write(img_data, arcname=img_name)
            os.remove(img_data)


    with open(os.path.join(os.getcwd(),f'generated_images/{date_today}_images.zip'), "rb") as fp:
        btn_download = st.download_button(
            label="Download ZIP",
            data=fp,
            file_name=f"{date_today}_images.zip",
            mime="application/zip"
        )

# btn_dlt_all_data = st.button("Delete all data")

# def delete_files_in_directory(directory_path):
#    try:
#      files = os.listdir(directory_path)
#      for file in files:
#        file_path = os.path.join(directory_path, file)
#        if os.path.isfile(file_path):
#          os.remove(file_path)
#      st.markdown("All files deleted successfully.")
#    except OSError:
#      st.markdown("Error occurred while deleting files.")

# # Delete all generated data
# if btn_dlt_all_data:
#     directory_path = os.path.join(os.getcwd(),f'generated_images')
#     delete_files_in_directory(directory_path)

st.subheader("Add URL for company logo")
st.markdown("This will replace the old url in the database. Add carefully.")
company_name_input = st.text_input("Enter company name")
company_name_input = company_name_input.strip().lower()
logo_url_input = st.text_input("Enter URL of logo")
logo_url_input = logo_url_input.strip().lower()
btn_add_company_logo = st.button("Add Company Logo URL")

# Delete all generated data
if btn_add_company_logo:
    company_logos[company_name_input] = logo_url_input
    if company_name_input != "" and logo_url_input != "":
        with open(os.path.join(os.getcwd(),f'data/company_logo.csv'), 'w',newline='') as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in company_logos.items():
                writer.writerow([key, value])
    else:
        st.markdown("Enter valid company name and URL")

    
