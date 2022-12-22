from PIL import Image

import argparse

#
#  pymag.py - mag format image file encoder in Python
#  https://github.com/tantanGH/pymag/
#
#  implemented based on the below mag format specifications:
#  MAGBIBLE.DOC (Mar.19,1991) by Woddy RINN
#

# command line parameters
parser = argparse.ArgumentParser()
parser.add_argument("infile",help="input image filename")
parser.add_argument("outfile",help="output image filename")
parser.add_argument("-x",help="output image width",type=int,default=768)
parser.add_argument("-y",help="output image height",type=int,default=512)
parser.add_argument("-c",help="output image colors",type=int,default=16,choices=[16,256])
parser.add_argument("-u",help="output mag user",type=str,default="pymag")
parser.add_argument("-m",help="output mag memo",type=str,default="")
parser.add_argument("-q",help="quantize method",type=int,default=1,choices=[0,1,2,3])
parser.add_argument("-d",help="dithering",type=int,default=1,choices=[0,1])
parser.add_argument("-k",help="k-means",type=int,default=100)
args = parser.parse_args()

# input image file name
input_image_name = args.infile

# output image file name, size and colors
output_image_name = args.outfile
output_size_x = args.x
output_size_y = args.y
output_colors = args.c

# memo
memo = args.m

# pixel size
pixel_size = 2 if ( output_colors == 256 ) else 4

# quantize parameters
quantize_method = args.q
quantize_dither = args.d
quantize_kmeans = args.k  

# load, resize and convert source image to raw bytes
raw_image = Image.open(input_image_name) \
                 .resize((output_size_x,output_size_y)) \
                 .quantize(colors=output_colors, method=quantize_method, kmeans=quantize_kmeans, dither=quantize_dither)

raw_image_bytes = raw_image.tobytes()
raw_image_pallet = raw_image.getpalette()

# mag constant parameters
scan_offset_x = [  0, -1, -2, -4,  0, -1,  0, -1, -2,  0, -1, -2,  0, -1, -2,   0 ]
scan_offset_y = [  0,  0,  0,  0, -1, -1, -2, -2, -2, -4, -4, -4, -8, -8, -8, -16 ]   
scan_order    = [  1,  4,  5,  6,  7,  9, 10,  2,  8, 11, 12, 13, 14,  3, 15 ]

# pixel data encoding
output_pixels_x = output_size_x // pixel_size   # with cropping
raw_flag_buffer = [ 0 ] * ( output_size_y * output_pixels_x )
pixel_buffer = []

for y in range( output_size_y ):
    for x in range( output_pixels_x ):
    
        current_pixel = ( raw_image_bytes[ y * output_size_x + x * 4 + 0 ] & 0xf ) << 12 | \
                        ( raw_image_bytes[ y * output_size_x + x * 4 + 1 ] & 0xf ) <<  8 | \
                        ( raw_image_bytes[ y * output_size_x + x * 4 + 2 ] & 0xf ) <<  4 | \
                        ( raw_image_bytes[ y * output_size_x + x * 4 + 3 ] & 0xf ) if ( pixel_size == 4 ) else \
                        ( raw_image_bytes[ y * output_size_x + x * 2 + 0 ] & 0xff ) << 8 | \
                        ( raw_image_bytes[ y * output_size_x + x * 2 + 1 ] & 0xff ) 

        current_flag = 0

        for s in scan_order:
            scan_x = x + scan_offset_x[ s ]
            scan_y = y + scan_offset_y[ s ]
            if ( scan_x < 0 or scan_y < 0 ):
                continue

            scan_pixel = ( raw_image_bytes[ scan_y * output_size_x + scan_x * 4 + 0 ] & 0xf ) << 12 | \
                         ( raw_image_bytes[ scan_y * output_size_x + scan_x * 4 + 1 ] & 0xf ) <<  8 | \
                         ( raw_image_bytes[ scan_y * output_size_x + scan_x * 4 + 2 ] & 0xf ) <<  4 | \
                         ( raw_image_bytes[ scan_y * output_size_x + scan_x * 4 + 3 ] & 0xf ) if ( pixel_size == 4 ) else \
                         ( raw_image_bytes[ scan_y * output_size_x + scan_x * 2 + 0 ] & 0xff ) << 8 | \
                         ( raw_image_bytes[ scan_y * output_size_x + scan_x * 2 + 1 ] & 0xff )

            if ( current_pixel == scan_pixel ):
                current_flag = s
                break

        raw_flag_buffer[ y * output_pixels_x + x ] = current_flag
        if ( current_flag == 0 ) :
            pixel_buffer.append(( current_pixel & 0xff00 ) >> 8 )
            pixel_buffer.append( current_pixel & 0xff )

# flag data preprocessing (xor)
xor_flag_buffer = [ 0 ] * ( output_size_y * output_pixels_x )
for y in reversed( range( output_size_y )):
    for x in range( output_pixels_x ):
        f0 = raw_flag_buffer[ ( y - 0 ) * output_pixels_x + x ]
        f1 = raw_flag_buffer[ ( y - 1 ) * output_pixels_x + x ] if ( y > 0 ) else 0
        xor_flag_buffer[ y * output_pixels_x + x ] = f0 ^ f1

# flag data encoding
flag_buffer_a = [ 0 ] * ( output_size_y * ( output_pixels_x // 2 ))
flag_buffer_b = []
for y in range( output_size_y ):
    for x in range( output_pixels_x // 2 ):
        f0 = xor_flag_buffer[ y * output_pixels_x + x * 2 + 0 ]
        f1 = xor_flag_buffer[ y * output_pixels_x + x * 2 + 1 ]
        if ( f0 == 0 and f1 == 0 ):
            flag_buffer_a[ y * ( output_pixels_x // 2 ) + x ] = 0
        else:
            flag_buffer_a[ y * ( output_pixels_x // 2 ) + x ] = 1
            flag_buffer_b.append(( f0 & 0xf ) << 4 | ( f1 & 0xf ))

# flag data bytes A
flag_data_bytes_a = bytearray( len( flag_buffer_a ) // 8 )
for i in range( len( flag_data_bytes_a )):
    flag_data_bytes_a[i] = ( flag_buffer_a [ i * 8 + 0 ] & 1 ) << 7 | \
                           ( flag_buffer_a [ i * 8 + 1 ] & 1 ) << 6 | \
                           ( flag_buffer_a [ i * 8 + 2 ] & 1 ) << 5 | \
                           ( flag_buffer_a [ i * 8 + 3 ] & 1 ) << 4 | \
                           ( flag_buffer_a [ i * 8 + 4 ] & 1 ) << 3 | \
                           ( flag_buffer_a [ i * 8 + 5 ] & 1 ) << 2 | \
                           ( flag_buffer_a [ i * 8 + 6 ] & 1 ) << 1 | \
                           ( flag_buffer_a [ i * 8 + 7 ] & 1 )

# flag data bytes B
flag_data_bytes_b = bytes(flag_buffer_b)
    
# pixel data bytes
pixel_data_bytes = bytes(pixel_buffer)
            
# pallet data bytes
pallet_data_bytes = bytearray( 3 * output_colors )
for i in range( output_colors ):
    pallet_g = raw_image_pallet[ i * 3 + 1 ]
    pallet_r = raw_image_pallet[ i * 3 + 0 ]
    pallet_b = raw_image_pallet[ i * 3 + 2 ]
    pallet_data_bytes[ i * 3 + 0 ] = pallet_g
    pallet_data_bytes[ i * 3 + 1 ] = pallet_r
    pallet_data_bytes[ i * 3 + 2 ] = pallet_b

# mag check data + comment
mag_check_data   = "MAKI02  "             # 8 bytes
mag_machine_code = "PYTN "                # 5 bytes 
mag_user_name    = "pymag              "  # 19 bytes
mag_memo         = f"{memo}\x1A"          # variable + EOF(0x1A)

check_data_bytes = bytes(mag_check_data + \
                         mag_machine_code + \
                         mag_user_name + \
                         mag_memo, 'ascii')

# mag header
header_top          = 0x00
header_machine_code = 0x00
header_machine_flag = 0x00
screen_mode         = 0x80 if ( output_colors == 256 ) else 0x00

header_data_bytes = bytes([header_top, \
                           header_machine_code, \
                           header_machine_flag, \
                           screen_mode])

# position data
pos_x0 = 0
pos_y0 = 0
pos_x1 = ( output_pixels_x * pixel_size ) - 1
pos_y1 = output_size_y - 1

pos_data_bytes = pos_x0.to_bytes(2,'little') + \
                 pos_y0.to_bytes(2,'little') + \
                 pos_x1.to_bytes(2,'little') + \
                 pos_y1.to_bytes(2,'little')

# offset data
flag_a_offset = 32 + len(pallet_data_bytes)
flag_b_offset = flag_a_offset + len(flag_data_bytes_a)
flag_b_size   = len(flag_data_bytes_b)
pixel_offset  = flag_b_offset + flag_b_size
pixel_size    = len(pixel_data_bytes)

offset_data_bytes = flag_a_offset.to_bytes(4,'little') + \
                    flag_b_offset.to_bytes(4,'little') + \
                    flag_b_size.to_bytes(4,'little') + \
                    pixel_offset.to_bytes(4,'little') + \
                    pixel_size.to_bytes(4,'little')

# save as an image file
with open(output_image_name,'bw') as f:
    f.write(check_data_bytes)
    f.write(header_data_bytes)
    f.write(pos_data_bytes)
    f.write(offset_data_bytes)
    f.write(pallet_data_bytes)
    f.write(flag_data_bytes_a)
    f.write(flag_data_bytes_b)
    f.write(pixel_data_bytes)
