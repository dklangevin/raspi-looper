import usb.core
import usb.util

dev = usb.core.find(idVendor=0x08bb, idProduct=0x2902)

# for bRequest in range(255):
#     try:
#         ret = dev.ctrl_transfer(0xC0, bRequest, 0, 0, 1024)
#         print("bRequest ", bRequest) 
#         print(ret)
#     except:
#         # failed to get data for this request
#         pass

# exit()

if dev.is_kernel_driver_active(1):
    dev.detach_kernel_driver(1)

configuration = dev.get_active_configuration()
interface = configuration[(1, 1)]
print(interface)


endpoint = interface[0]

r = dev.read(endpoint, 10)

print('Length:', len(r))