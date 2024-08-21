from flask import Flask, render_template, request
import hashlib
import io
from PIL import Image
import cv2
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def upload_and_compare():
    
    if request.method == 'POST':
        # Get the uploaded images
        image1 = request.files['image1']
        image2 = request.files['image2']
        # image2 = request.files['image2']
        # Save the images to the local directory
        image1.save('static/img/image1.png')
        image2.save('static/img/image2.png')
        image1.save('image1.png')
        image2.save('image2.png')


    
        # Load the image
        image = cv2.imread('static/img/image1.png')
        topleftimg,bottomrightimg=divide_image(image)
        halfbinary1= cv2.imencode('.png',topleftimg)[1].tobytes().hex()
        halfbinary2= cv2.imencode('.png',bottomrightimg)[1].tobytes().hex()


        zero_count=count_zeros(halfbinary1)
        ones_count=count_ones(halfbinary2)

        
    

        # Compare the number of pixels
        pixels_image1 = get_pixel_count('static/img/image1.png')
        pixels_image2 = get_pixel_count('static/img/image2.png')




        if pixels_image1 == pixels_image2:
           resultp = 1
        else:
           resultp = -1


        # Read the image files
        img1 = Image.open(image1)
        img2 = Image.open(image2)

         
        # Compare the metadata of the images
        is_same_metadata = compare_metadata(img1, img2)


        # Convert images to binary
        binary1 = image_to_binary(img1)
        binary2 = image_to_binary(img2)


        zero_countfull= count_zerosfull(binary1)
        refid=zero_count+(pixels_image1-zero_countfull)-ones_count

        

        # Compare the binary codes
        binary_comparison = compare_binary(binary1, binary2)

        # Calculate the hash values
        hash1 = calculate_hash(binary1)
        hash2 = calculate_hash(binary2)

        # Compare the hash values
        hash_comparison = compare_hashes(hash1, hash2)

        # Determine the overall result
        if binary_comparison == 1 and hash_comparison == 1 and resultp==1 :
            return render_template('true.html',image1=image1, image2=image2, is_same_metadata=is_same_metadata,refid=refid) 
        else:

            return render_template('false.html',image1=image1, image2=image2, is_same_metadata=is_same_metadata)

        

    return render_template('upload.html')
@app.route('/keysearch')
def keysearch():
    return render_template('keysearch.html')

@app.route('/search', methods=['GET', 'POST'])
def key_search():
    if request.method == 'POST':
        # Get the uploaded image and text input
        image = request.files['image']
        text = request.form['text']

        text=int(text)

        # Save the image to the local directory
        image.save('static/img/search_image.png')

               
        image1 = cv2.imread('static/img/search_image.png')

        topleftimg,bottomrightimg=divide_image(image1)
        halfbinary1= cv2.imencode('.png',topleftimg)[1].tobytes().hex()
        halfbinary2= cv2.imencode('.png',bottomrightimg)[1].tobytes().hex()
        

        zero_count=count_zeros(halfbinary1)
        ones_count=count_ones(halfbinary2)
        pixels_image1 = get_pixel_count('static/img/search_image.png')
        img1 = Image.open(image)
        binary1 = image_to_binary(img1)
        zero_countfull= count_zerosfull(binary1)
        refid=zero_count+(pixels_image1-zero_countfull)-ones_count
        refid=int(refid)
        if text== refid :
            return render_template('true1.html', refid=refid,text=text) 
        else:

            return render_template('false1.html',text=text) 
        
       
     
        

        # Return the results to the user
        return render_template('keysearch.html', image='search_image.png', text=text)

    return render_template('keysearch.html')


def image_to_binary(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def compare_binary(binary1, binary2):
    return 1 if binary1 == binary2 else -1

def calculate_hash(binary):
    return hashlib.sha256(binary).hexdigest()

def compare_hashes(hash1, hash2):
    return 1 if hash1 == hash2 else -1

def get_pixel_count(image_path):
    with open(image_path, 'rb') as file:
        file.seek(2)  # Skip the first two bytes (signature)
        width = int.from_bytes(file.read(4), 'big')
        height = int.from_bytes(file.read(4), 'big')
        return width * height
    
def compare_metadata(image1, image2):
          metadata1 = image1._getexif()
          metadata2 = image2._getexif()

          return 1 if metadata1 == metadata2 else -1
def divide_image(image):
    # Get the dimensions of the image
        height, width, _ = image.shape

        # Divide the image into four equal parts
        half_height = height // 2
        half_width = width // 2

        top_left = image[:half_height, :half_width]
        top_right = image[:half_height, half_width:]
        bottom_left = image[half_height:, :half_width]
        bottom_right = image[half_height:, half_width:]

        return top_left,bottom_right

def count_zeros(halfbinary):
        count = 0
        for bit in halfbinary:
           if bit == '0':
             count += 1
        return count
def count_zerosfull(fullbinary):
        count = 0
        for bit in fullbinary:
           if bit == '0':
             count += 1
        return count
def count_ones(fullbinary):
        count = 0
        for bit in fullbinary:
           if bit == '1':
             count += 1
        return count



   

if __name__ == '__main__':
    app.run(debug=True)