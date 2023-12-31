import os
import hashlib
import sys
import shutil

hash_dict = {}
size_dict = {}


def find_duplicates(directory, diff_):
    for root, dirs, files_ in os.walk(directory, topdown=True):
        for filename in files_:
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


def rd(file_) -> None:
    if not os.path.exists(file_):
        return
    with open(file_, 'r+', encoding='utf-8', newline='\n') as f:
        data = f.readlines()
        new_data = sorted(set(data), key=data.index)
        if len(new_data) == len(data):
            print("No need to handle")
            return
        f.seek(0)
        f.truncate()
        f.writelines(new_data)
    del data, new_data


def usage():
    print('''
    Folder Differ
      Find duplicate files in the folder and delete other identical files
      Author:ColdWindScholar(3590361911@qq.com)
      Github:https://github.com/ColdWindScholar/folder_diff
    Usages:
     Find duplicate files:
       diff.py diff [folder path]  [diff file]
     recover del files:
       diff.py recv [diff file path]
     Merge diff files:
       diff.py merge [file1] [file2] [...] [new_diff]
    ''')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    if sys.argv[1] == 'diff':
        path = os.path.abspath(sys.argv[2])
        if len(sys.argv) > 3:
            diff_file = os.path.abspath(sys.argv[3])
        else:
            diff_file = os.path.dirname(path) + os.sep + os.path.basename(path)+".diff"
        print(f"Diff File:{diff_file}")
        with open(diff_file, 'w') as diff:
            find_duplicates(path, diff)
    elif sys.argv[1] == 'recv':
        path = os.path.abspath(sys.argv[2])
        recover(path)
    elif sys.argv[1] == 'merge':
        if len(sys.argv) < 4:
            print("At least two files are required!")
            usage()
            sys.exit(1)
        *files, new = sys.argv[2:]
        with open(new, 'w+') as new_diff:
            for old_ in files:
                print(f"Merge {old_} to {new}")
                with open(old_, 'r') as old:
                    new_diff.writelines(old.readlines())
        rd(new)
    input("Done！")
