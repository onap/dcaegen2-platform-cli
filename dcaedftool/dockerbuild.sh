# it assumes docker toolkit is installed.  It was tested on Windows
# A reboot might be necessary if failures persist 
docker-machine  rm box  -f
docker-machine create box
eval $('C:/Program Files/Docker Toolbox/docker-machine.exe' env box)
ng build --prod --output-hashing none
docker rm dcaedf
docker build -t dcaedf:1.0.1  .
