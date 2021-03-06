#!/usr/bin/python
import random
import sys
import struct

# Clean UP the standard PE Dos Stub
# Implement the Bonneteau Cypher, no entropy impact
# Variable Keylen
# Ex :
#    Key =  13402
#    Data =  01234 56789
#    Result = 1340268957

if __name__ == '__main__':
  # Charge le payload
  try:
    print ('* Loading payload: %s' % sys.argv[1])
    f = open(sys.argv[1],'r')
    payload = bytearray(f.read())
    f.close()
    payload_len = len(payload)
    print ('* Payload len: %d bytes' % (payload_len))
  except:
    print('** Error opening file')
    exit(1)
  
  # Clean UP DOS Stub
  S = struct.Struct('<H')
  idxdospay = S.unpack_from(buffer(bytearray(payload[0x18:0x18+2])))[0] 
  S = struct.Struct('<I')
  lendospay = (  S.unpack_from(buffer(bytearray(payload[0x3c:0x3c+4])))[0] - idxdospay)  
  print ('* Dos Code at 0x%X for 0x%X bytes' % (idxdospay,lendospay))
  dosstub=bytearray()
  IDX=0
  
  dospay = 0xb8,0x00,0x4c,0xcd,0x21
  dospay = ""
  for I in range(0,idxdospay):
    dosstub[I:I+1] = payload[I:I+1]
    IDX=IDX+1
  for I in ( dospay ):  # mov ax,0x4c00; Int 0x21
    dosstub.append(I)
    IDX=IDX+1
  for I in range(0,lendospay - len (dospay)):
    dosstub.append(0x00)
    IDX=IDX+1
  for I in range(IDX,payload_len):
    dosstub[I:I+1] = payload[I:I+1]
  
  
  payload = dosstub 

  # Choisis une taille de BBOX de 128 a 256 bytes
  bboxlen = random.randrange(128)+128
 
  #payload = [ 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
  #payload_len = len (payload)
  #bboxlen = random.randrange(5)+1
  print ('* BBox Len: %d' % bboxlen)


  # Genere le BBox Array
  bboxarray=[]
  for i in range(0,bboxlen):
    bboxarray.append(i)
  random.shuffle(bboxarray)
  

  #bboxarray = [4,2,3,1,0]
  #bboxlen = 5
  #print bboxarray

  opayload = bytearray(bboxarray)

  fullrow = payload_len // bboxlen 
  restrow = payload_len % bboxlen
  
  print ('* Ready to Process %dx%d bytes row and %d bytes' % (fullrow,bboxlen,restrow)) 
  
  if not restrow == 0:
    print ('* Adding %d padding bytes' % (bboxlen-restrow))
    for i in range(0,bboxlen-restrow):
      payload.append(0x00)
    payload_len = payload_len + (bboxlen- restrow)
    fullrow = payload_len // bboxlen 
    restrow = payload_len % bboxlen
    print ('* Final Process %dx%d bytes row and %d bytes' % (fullrow,bboxlen,restrow)) 
   
  for BBraw in range(0,fullrow):
    for I in bboxarray:
      opayload.append(payload[(BBraw*bboxlen)+I])
     # print hex(payload[(BBraw*bboxlen)+I]) ,
    #print ""
  #opayload = payload
 
  out = bytearray(opayload)
  

  with open('payload.bin',"w") as f:
    f.write(out)

  include = ('PELEN dd 0x%X ; PE Len\n' % payload_len)
  include = include + ('BBLEN db 0x%X ; BBox Key Len\n' % bboxlen) 
  include = include + ('EPELEN equ 0x%X; PE Len equ\n' % payload_len)
  include = include + ('RANDOMs equ 0x%X ; Random 8 bits\n' % random.randrange(0x16))
  include = include + ('RANDOM8 equ 0x%X ; Random 8 bits\n' % random.randrange(0xff))
  include = include + ('RANDOM16 equ 0x%X ; Random 8 bits\n' % random.randrange(0xffff))
  include = include + ('RANDOM32 equ 0x%X ; Random 8 bits\n' % random.randrange(0xffffffff)) 
  with open('payload.inc', 'w') as f:
     f.write(include)

