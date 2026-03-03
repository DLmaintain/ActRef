import csv


ground_truth = []  
detection_result = []  
# The out list contains commits that out of length, we exclude these when calculate the P/R/F1
DS_out = ['6b106ab4ec9a1c0eb3e24ae590ce63f84022ad40', '09fe3365beaf43b9d7979399ce10efd086717b24', '48c1c96ac4cfec5580a5feb7eb7ef7c25c6db234', '667d09e75837aa66b523bf29b8572950333857e0', '8c70687b9e5f506169bd20736bd5a6bbd6cba0a5', 'ef86d2e73e7ce03c4184a04a336d96caf661269a', '83a2e7f1e1c8c65add9eae27e266881159502ab8', '73a5213bfbe7c40079102dfebe0cc12ab17135be', '315719efa3fa6a8fbb599ffc9297899671e6d1bc', 'c863dde7c5bffc05d716bc0132a1dd55ceaa42a0', '63352897d1db6a7a009a1097ee9b16be13fc53b3', 'a5103909bb43f6e9d655587949b54cbd95abbb18', 'df3053cbc34b7d8fbb592692f7febec109bc5df5', '1b1c5dfe4ad278aa04c36df4805c2602610a0ec0', 'b55913abde69a95155de70ff6b4dd8fd3d51e998', '8854a03526f72193a53264246032f7a51bfe0fda', 'be65ce986a45bf2f35b5494db3fa6e993b905aeb', '3e48bcfabca9fa430135cd1e6a737fc365943391', '2cf63e796423fbe0af0eb465c8195f47b658c824', '57a45aaf7e82a826e1bffb133c328f913844bd4c', 'ec151fdd3aee0c0e1755de860d5f6324fa58a7c3']

GPT_out = ['8c70687b9e5f506169bd20736bd5a6bbd6cba0a5', '315719efa3fa6a8fbb599ffc9297899671e6d1bc', 'a5103909bb43f6e9d655587949b54cbd95abbb18', '1b1c5dfe4ad278aa04c36df4805c2602610a0ec0', 'b55913abde69a95155de70ff6b4dd8fd3d51e998']
types = ['Move Method','Extract Method', 'Inline Method','Rename Method', 
         'Move Class','Extract Class','Inline Class','Rename Class',
         'Move Module',  'Extract Module',   'Inline Module','Rename Module', 
         'Extract Variable',  'Inline Variable'
         ,  'Rename Variable'
]
FPs = []

print('DeepSeek Reasoner: ')

with open('data.csv', 'r') as gt_file:
  
    final_list = []
    ignore = ['Rename Parameter']
    reader = csv.reader(gt_file)
    next(reader)  
    for row in reader:

        if row[0] in DS_out:
            continue
        if row[6] == 'FP':
            continue
        if row[1] not in types:
            continue
        final_list.append(row[0])
        if row[4]:
            sha, ref_type, src, dst = row[0], row[1], row[4], row[5]
        else:
   
            sha, ref_type, src, dst = row[0], row[1], row[3][:6], row[3][-6:]
        if 'Module' in row[1]:
            tmp = row[4].split('/')

            src = tmp[-1]
            tmp2 = row[5].split('.py')
            tmp3 = tmp2[0].split('/')
            dst = tmp3[-1]
  
        ground_truth.append({'sha': sha, 'refactoring_type': ref_type, 'src': src, 'dst': dst})



with open('gpt_refactorings.csv', 'r') as dr_file:
    reader = csv.reader(dr_file)

    for row in reader:
        ref_type = row[1]
        if 'Function' in ref_type:
            ref_type.replace('Function', 'Method')
        if 'Methods' in ref_type:
            ref_type.replace('Methods', 'Method')

        if ref_type not in types:
            continue
        if row[0] not in final_list:

            continue
        sha = row[0]

        description = row[2]
        detection_result.append({'sha': sha, 'refactoring_type': ref_type, 'description':description})
 
print(len(detection_result))

precision_per_type = {t: {'TP': 0, 'FP': 0, 'P':0} for t in types}
recall_per_type = {t: {'TP': 0, 'FN': 0,'R':0} for t in types}


for result in detection_result:
    sha_r, ref_type_r, description = result['sha'], result['refactoring_type'], result['description']
    found_match = False
    for gt in ground_truth:
        sha_gt, ref_type_gt, src_gt, dst_gt = gt['sha'], gt['refactoring_type'], gt['src'], gt['dst']
        if sha_r == sha_gt and ref_type_r == ref_type_gt:

            
            precision_per_type[ref_type_r]['TP'] += 1
            recall_per_type[ref_type_r]['TP'] += 1
            found_match = True
            break

    if not found_match:
        tmp = [sha_r,ref_type_r,description]
        FPs.append(tmp)

        precision_per_type[ref_type_r]['FP'] += 1 


for gt in ground_truth:
    sha_gt, ref_type_gt, src_gt, dst_gt = gt['sha'], gt['refactoring_type'], gt['src'], gt['dst']
    found_match = False
    for result in detection_result:
        sha_r, ref_type_r, description = result['sha'], result['refactoring_type'], result['description']
        if sha_r == sha_gt and ref_type_r == ref_type_gt:
            found_match = True
            break
    if not found_match:
        recall_per_type[ref_type_gt]['FN'] += 1  
F = []

for ref_type in types:
    tp = precision_per_type[ref_type]['TP']
    fp = precision_per_type[ref_type]['FP']
    fn = recall_per_type[ref_type]['FN']
    
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    F1 = 2 * recall * precision/(precision + recall) if precision+recall >0 else 0
    precision_per_type[ref_type]['P'] = precision
    recall_per_type[ref_type]['R'] = recall
    F.append(F1)
    
    print(f'{ref_type}: Precision = {precision:.3f}, Recall = {recall:.3f}, F1 = {F1:.3f} TP = {tp}, FP = {fp}, FN = {fn}')



total_tp = sum([precision_per_type[t]['TP'] for t in types])
total_fp = sum([precision_per_type[t]['FP'] for t in types])
total_fn = sum([recall_per_type[t]['FN'] for t in types])

overall_precision = total_tp / (total_tp + total_fp) if total_tp + total_fp > 0 else 0
overall_recall = total_tp / (total_tp + total_fn) if total_tp + total_fn > 0 else 0

overall_f1 = 2 * overall_precision * overall_recall / (overall_recall + overall_precision)
print(f'Overall: Precision = {overall_precision:.3f}, Recall = {overall_recall:.3f}, F1 = {overall_f1:.3f}, total_tp = {total_tp}, total_fp = {total_fp}, total_fn = {total_fn}')



macro_f1 = sum(F)/len(F)
micro_precision = total_tp / (total_tp + total_fp)
micro_recall = total_tp / (total_tp + total_fn)
micro_f1 = 2 * (micro_precision * micro_recall) / (micro_precision + micro_recall)

print(f'MACRO_F1 = {macro_f1}, MICRO_F1 = {micro_f1}')

with open('GPT_FPs.csv','w') as f:
    csv_writter = csv.writer(f)
    for i in FPs:
        csv_writter.writerow(i)