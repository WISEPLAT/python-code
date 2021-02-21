remove this line to prevent run without your config!!! удалите эту строку для предотвращения запуска без вашей настройки!!!

import os
# in terminal run command: pip install cryptography
from cryptography.fernet import Fernet

scan_dir_to_encrypt_decrypt = 'm:\\my_super_files\\'

key = Fernet.generate_key()
if not os.path.exists('my_key.txt'):
    with open('my_key.txt', 'wb') as f:
        f.write(key)
else:
    key = open('my_key.txt', 'rb').read()
print(key)
cipher = Fernet(key)

encrypt_yes = True

if encrypt_yes:
    with os.scandir(path=scan_dir_to_encrypt_decrypt) as it:
        for entry in it:
            if not entry.is_file():
                print("dir:\t" + entry.name)
            else:
                read_file = open(scan_dir_to_encrypt_decrypt+entry.name, 'rb').read()
                encrypted_file_content = cipher.encrypt(read_file)
                with open(scan_dir_to_encrypt_decrypt+entry.name, 'wb') as f:
                    f.write(encrypted_file_content)
                print("file encrypted:\t" + entry.name)
else:
    with os.scandir(path=scan_dir_to_encrypt_decrypt) as it:
        for entry in it:
            if not entry.is_file():
                print("dir:\t" + entry.name)
            else:
                encrypted_file_content = open(scan_dir_to_encrypt_decrypt+entry.name, 'rb').read()
                file_content = cipher.decrypt(encrypted_file_content)
                with open(scan_dir_to_encrypt_decrypt+entry.name, 'wb') as f:
                    f.write(file_content)
                print("file decrypted:\t" + entry.name)

