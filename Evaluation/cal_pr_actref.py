import csv


ground_truth = []  
detection_result = []  



types = ['Move Method','Extract Method', 'Inline Method','Rename Method', 'Rename Class',
         'Move Class','Extract Class','Inline Class',
         'Move Module',  'Extract Module',   'Inline Module','Rename Module', 
         'Extract Variable',  'Inline Variable'
         ,  'Rename Variable'
]

with open('data.csv', 'r') as gt_file:
   
    final_list = []

    reader = csv.reader(gt_file)

    for row in reader:
        sha = row[0]
        if row[1] not in types:
            continue
        final_list.append(sha)
        ref_type, description, url = row[1], row[3]+row[4]+row[5], row[2]
        if row[6] != 'TP' and row[6] != 'FN':
            continue

        ground_truth.append({'sha': sha, 'refactoring_type': ref_type, 'description': description, 'url': url})


with open('actref.csv', 'r') as dr_file:
    reader = csv.reader(dr_file)
    ignore = ['Rename Parameter']
    for row in reader:
        if row[1] in ignore:
            continue
        if row[0] not in final_list:
            continue
        if row[1] not in types:

            continue
        if len(row) == 8:
            sha, ref_type, src, dst, ol, nl = row[0], row[1], row[2].replace('#','/'), row[3].replace('#','/'), row[6], row[7]
        else:
            sha, ref_type, src, dst, ol, nl = row[0], row[1], row[2].replace('#','/'), row[3].replace('#','/'), 'None', 'None'
        detection_result.append({'sha': sha, 'refactoring_type': ref_type, 'src': src, 'dst': dst, 'old_location': ol, 'new_location': nl})

tp_items = []  
fp_items = []  
fn_items = []  


precision_per_type = {t: {'TP': 0, 'FP': 0} for t in types}
recall_per_type = {t: {'TP': 0, 'FN': 0} for t in types}


for result in detection_result:
    sha_r, ref_type_r, src_r, dst_r = result['sha'], result['refactoring_type'], result['src'], result['dst']
    found_match = False
    for gt in ground_truth[:]:
        sha_gt, ref_type_gt, desc_gt, url = gt['sha'], gt['refactoring_type'], gt['description'], gt['url']
        if sha_r == sha_gt and ref_type_r == ref_type_gt:
            if src_r in desc_gt.replace('#','/') and dst_r in desc_gt.replace('#','/'): 
                precision_per_type[ref_type_r]['TP'] += 1
                recall_per_type[ref_type_r]['TP'] += 1
                found_match = True
                tp_items.append({**result, 'match_type': 'TP','url':url})
                break
    if not found_match:
        if ref_type_r not in types:
            continue
        precision_per_type[ref_type_r]['FP'] += 1 
        fp_items.append({**result, 'match_type': 'FP'})

for gt in ground_truth:
    sha_gt, ref_type_gt, desc_gt, url = gt['sha'], gt['refactoring_type'], gt['description'], gt['url']
    found_match = False
    for result in detection_result:
        sha_r, ref_type_r, src_r, dst_r = result['sha'], result['refactoring_type'], result['src'], result['dst']
        if sha_r == sha_gt and ref_type_r == ref_type_gt:
            if src_r in desc_gt.replace('#','/') or dst_r in desc_gt.replace('#','/'):
                found_match = True
                
                break
    if not found_match:
        recall_per_type[ref_type_gt]['FN'] += 1  
        fn_items.append({**gt, 'match_type': 'FN','url':url})
  
F =[]

for ref_type in types:
    tp = precision_per_type[ref_type]['TP']
    fp = precision_per_type[ref_type]['FP']
    fn = recall_per_type[ref_type]['FN']
    if tp == 0:
        print(ref_type)
        continue
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1 = 2 * recall * precision/(precision + recall)  
    F.append(f1)  
    print(f'{ref_type}: Precision = {precision:.3f}, Recall = {recall:.3f}, F1 = {f1:.2f}, total = {fn + tp}, TP = {tp}, FP = {fp}, FN = {fn}')

total_tp = sum([precision_per_type[t]['TP'] for t in types])
total_fp = sum([precision_per_type[t]['FP'] for t in types])
total_fn = sum([recall_per_type[t]['FN'] for t in types])

overall_precision = total_tp / (total_tp + total_fp) if total_tp + total_fp > 0 else 0
overall_recall = total_tp / (total_tp + total_fn) if total_tp + total_fn > 0 else 0

print(f'Overall: Precision = {overall_precision:.3f}, Recall = {overall_recall:.3f}, total = {total_fn + total_tp}, total_tp = {total_tp},  total_fp = {total_fp}, total_fn = {total_fn}')

macro_f1 = sum(F)/len(F)
micro_precision = total_tp / (total_tp + total_fp)
micro_recall = total_tp / (total_tp + total_fn)
micro_f1 = 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall)

print(f'MACRO_F1 = {macro_f1}, MICRO_F1 = {micro_f1}')

