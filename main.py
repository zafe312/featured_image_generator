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

company_logos = {
                 'Apple':'https://i.pinimg.com/736x/4f/39/fc/4f39fc3681b24694bfc353a5e24a9a2c.jpg',
                 'Google':'https://upload.wikimedia.org/wikinews/en/0/0c/Google_logo_png.png',
                 'Pinterest':'https://pngimg.com/uploads/pinterest/pinterest_PNG4.png'
                 }

# company_names = ['Apple','Boat','Turing','Wipro','Google','Pinterest','Genpact']
# job_positions = ['Sales Manager','Trainee Engineer','Customer Service','Business Analyst','Data Entry Operator','Human Resources','Sales Account Executive']

button_clicked = st.button("Generate images")

generated_image_names = []

if os.path.isfile(os.path.join(os.getcwd(),f'generated_images/{date_today}_images.zip')):
    os.remove(os.path.join(os.getcwd(),f'generated_images/{date_today}_images.zip'))

if button_clicked:

    for i, company_name in enumerate(company_names):

        company_name = company_name.capitalize()
        
        template_number = np.random.choice([1,2,3])

        img1 = Image.open(os.path.join(os.getcwd(),f'featured_image_templates/featured_image_template_{template_number}.png'))
        try:
            # img2 = Image.open(os.path.join(os.getcwd(),f'company_logos/{company_name}_logo.png'))
            url = company_logos[company_name]
            response = requests.get(url)
            img2 = Image.open(BytesIO(response.content))
        except:
            st.markdown(f'No logo found for {company_name} in database. Check spelling or upload logo.')
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
        font = ImageFont.truetype("C:/Users/Admin/Downloads/hirelist/image_generation/fonts/Arial.ttf", 46)
        draw.text((100, 400),job_positions[i],(255,255,255),font=font)
        # draw.text((50, 200),job_positions[i],(255,25,255),font=font)
        
        image_name = f'{date_today}_{company_name}'
        if image_name + '.png' in generated_image_names:
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
