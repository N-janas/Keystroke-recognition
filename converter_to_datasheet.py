import os
import sys

pswd_pattern = ['f', 'j', 'shift', 'a', 'r', '@', 'shift', 's', 'shift', 'e', '6', '9']
# No special chars
pswd_chars = ['f', 'j', 'a', 'r', '@', 's', 'e', '6', '9']

def create_column_names(heading):
    yield heading+'_DD'
    yield heading+'_H'

def remove_empty(batches):
    # Remove empty list if one was created
    for batch in batches:
        if not batch:
            batches.remove(batch)

def write_content(batch, attempt, subject_id, delim):
    record = f'{subject_id},{attempt},' + ''.join([','.join(row.split(delim)[1:]) for row in batch])
    return record
        
# Check batch:
# 1. If Capital and Rightshift needs to be changed/deleted
# 2. If symbols that software didn't catch were put to file
# 3. If shifts are missing
def adjust_batch(batch, delim):
    # Because Capital is buggy, we have to manually adjust its position
    capitals = []
    for i, el in enumerate(batch):
        head = el.split(delim)[0]
        if head=='Capital':
            # If capital is found then get first data (as shift)
            # and drop next one (closing capital)
            cap = batch.pop(i)
            if len(capitals) < 2:
                capitals.append(cap)

            for j, el2 in enumerate(batch):
                if el2.split(delim)[0]=='Capital':
                    batch.pop(j)
                    break

    # If capitals were in batch
    if capitals:
        batch_headers = [b.split(delim)[0] for b in batch]
        i1 = batch_headers.index('J')
        i2 = batch_headers.index('S')

        batch.insert(i1+1, capitals[0])
        batch.insert(i2+2, capitals[1])

    # Change any right/left shift /capital to one consistent name
    for i, el in enumerate(batch):
        head = el.split(delim)[0]
        if head=='RightShift' or head=='Capital' or head=='LeftShift':
            batch[i] = delim.join(['Shift'] + el.split(delim)[1:])

    # Adjust mistakes with pswd_pattern string
    for i, el in enumerate(pswd_pattern):
        # Drop from list until the current character is the same as in the pattern pswd
        try:
            # Pop value that is not in pattern
            while batch[i].split(delim)[0].lower() != pswd_pattern[i]:
                current_header = batch[i].split(delim)[0].lower()
                # Basically if mistake is in pattern (while loop happened)
                # so if current header is shift (there are no shifts in pswd_chars) then pop it
                # If header is letter then if this letter is in pswd_chars (has to be software requires it)
                # then something had to be missed, so pswd_pattern[i] with NaN's is inserted
                if current_header in pswd_chars:
                    batch.insert(i, f'{pswd_pattern[i]}{delim}NaN{delim}NaN{delim}')
                else:
                    batch.pop(i)
                    
        except IndexError:
            print('')
    # Delete remaining symbols like 'Return' at the end 
    return batch[:len(pswd_pattern)]
            

def convert_to_csv(files_directory, delimeter, attempt_separator):
    # Create data sheet file based on pswd pattern
    with open('results.csv', 'w') as res:
        # Create column names and write them into file with separation
        columns = ['subject', 'attempt'] + [col_name for h in pswd_pattern for col_name in create_column_names(h)]
        res.write(','.join(columns))

    for subject_id, file in enumerate(os.listdir(files_directory)):
        with open(files_directory+file, 'r') as f:
            with open('results.csv', 'a+') as results:
                # Read file content
                file_content = f.readlines()
                # Clear lines from \n symbols
                file_content = [line.rstrip() for line in file_content]
                # Get indexes of separators
                sep_idxs = [idx for idx, el in enumerate(file_content) if el==attempt_separator]
                # Split lists by separator 
                batches = [file_content[i: j] for i, j in zip([0]+[idx+1 for idx in sep_idxs], sep_idxs+[len(file_content)])]
                remove_empty(batches)
                # Adding records from file
                for attempt, batch in enumerate(batches):
                    results.write('\n')
                    batch = adjust_batch(batch, delimeter)
                    results.write(write_content(batch, attempt, subject_id, delimeter))


def main(raw_data_dir='./raw_data/', delimeter=';', attempt_separator=':'):
    convert_to_csv(raw_data_dir, delimeter, attempt_separator)

if __name__=='__main__':
    if len(sys.argv) <= 1:
        main() 
    elif len(sys.argv) <= 4:
        main(*sys.argv[1:])
    else :
        print('Too many args')
