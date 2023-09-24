import os
import hashlib
import sys
import shutil

hash_dict = {}
size_dict = {}


def find_duplicates(directory, diff_):
    for root, dirs, files in os.walk(directory, topdown=True):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                size_dict[os.path.getsize(filepath)] = filepath
            except OSError:
                continue
            if not os.path.getsize(filepath) in size_dict:
                continue
            try:
                with open(filepath, 'rb') as f:
                    filehash = hashlib.md5(f.read()).hexdigest()
            except OSError:
                print(f"Cannot Hash {filepath}")
                continue

            if filehash in hash_dict:
                if filepath == hash_dict[filehash]:
                    continue
                print('Duplicate file found: {} == {}'.format(filepath, hash_dict[filehash]))
                try:
                    os.remove(filepath)
                except PermissionError:
                    print(f"Cannot Remove {filepath}")
                diff_.write(f'{hash_dict[filehash]} ==> {filepath}\n')
            else:
                print(f'Add hash [{filepath}] [{filehash}]')
                hash_dict[filehash] = filepath


def recover(file):
    with open(file, 'r') as f:
        for g in f.readlines():
            f, e = g.strip().split(' ==> ')
            if not os.path.exists(f):
                print("Missing {f}!")
                continue
            print(f"Copy {f} ==> {g}")
            try:
                shutil.copyfile(f, e)
            except OSError as e:
                print(f"Fail!{e}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("参数不足")
        sys.exit(1)
    if sys.argv[1] == 'diff':
        path = os.path.abspath(sys.argv[2])
        with open(path + os.sep + "diff", 'w') as diff:
            find_duplicates(path, diff)
    elif sys.argv[1] == 'recv':
        path = os.path.abspath(sys.argv[2])
        recover(path)
    input("Done！")
