echo
echo "============================="
echo "Checking for image updates..."
python check_image_updates.py python 3.7
python check_image_updates.py mongo 4.1.4
python check_image_updates.py nginx 1.15.5
echo "=============================="
echo
