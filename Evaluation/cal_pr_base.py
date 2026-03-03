import csv

# 初始化变量来存储标准集和检测结果
ground_truth = []  # 标准集列表
detection_result = []  # 检测结果列表

# 读取标准集文件
with open('baseline_list.csv', 'r') as gt_file:
    ignore = ['Rename Variable' , 'Move Variable','Inline Module', 'Rename Module','Extract Module','Move Module','Inline Class', 'Inline Variable']
    reader = csv.reader(gt_file)
    next(reader)  # 跳过头部
    for row in reader:
        if row[2] in ignore:
            continue
        sha, ref_type, description, url = row[0], row[2], row[4], row[3]
        ground_truth.append({'sha': sha, 'refactoring_type': ref_type, 'description': description, 'url': url})

# 读取检测结果文件
with open('test_simple_base_1024.csv', 'r') as dr_file:
    reader = csv.reader(dr_file)
    # next(reader)  # 跳过头部
    ignore = ['Rename Variable' , 'Move Variable','Inline Module', 'Rename Module','Extract Module','Move Module','Inline Class', 'Inline Variable']
    for row in reader:
        if row[1] in ignore:
            continue
        if len(row) == 8:
            sha, ref_type, src, dst, ol, nl = row[0], row[1], row[2], row[3], row[6], row[7]
        else:
            sha, ref_type, src, dst, ol, nl = row[0], row[1], row[2], row[3], 'None', 'None'
        detection_result.append({'sha': sha, 'refactoring_type': ref_type, 'src': src, 'dst': dst, 'old_location': ol, 'new_location': nl})

# 计算每种重构类型的 precision 和 recall
types = ['Extract Method', 'Extract Variable', 'Extract Class',  
         'Inline Method',
         'Rename Method', 'Rename Class',  
         'Rename Parameter',   'Move Class', 'Move Method']

# 初始化变量来计算每种类型的结果
precision_per_type = {t: {'TP': 0, 'FP': 0} for t in types}
recall_per_type = {t: {'TP': 0, 'FN': 0} for t in types}

# 比较检测结果与标准集，匹配 src 或 dst 到 description
for result in detection_result:
    sha_r, ref_type_r, src_r, dst_r = result['sha'], result['refactoring_type'], result['src'], result['dst']
    found_match = False
    for gt in ground_truth:
        sha_gt, ref_type_gt, desc_gt = gt['sha'], gt['refactoring_type'], gt['description']
        if sha_r == sha_gt and ref_type_r == ref_type_gt:
            if src_r in desc_gt or dst_r in desc_gt:  # 检查 src 或 dst 是否存在于描述中
                precision_per_type[ref_type_r]['TP'] += 1
                recall_per_type[ref_type_r]['TP'] += 1
                found_match = True
                break
    if not found_match:
        precision_per_type[ref_type_r]['FP'] += 1  # 检测到了错误的重构类型

# 检查标准集中是否有遗漏的重构类型（FN）
for gt in ground_truth:
    sha_gt, ref_type_gt, desc_gt = gt['sha'], gt['refactoring_type'], gt['description']
    found_match = False
    for result in detection_result:
        sha_r, ref_type_r, src_r, dst_r = result['sha'], result['refactoring_type'], result['src'], result['dst']
        if sha_r == sha_gt and ref_type_r == ref_type_gt:
            if src_r in desc_gt or dst_r in desc_gt:
                found_match = True
                break
    if not found_match:
        recall_per_type[ref_type_gt]['FN'] += 1  # 漏掉的重构类型

# 计算每种重构类型的 precision 和 recall
for ref_type in types:
    tp = precision_per_type[ref_type]['TP']
    fp = precision_per_type[ref_type]['FP']
    fn = recall_per_type[ref_type]['FN']
    
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    
    print(f'{ref_type}: Precision = {precision:.2f}, Recall = {recall:.2f}')

# 计算整体的 precision 和 recall
total_tp = sum([precision_per_type[t]['TP'] for t in types])
total_fp = sum([precision_per_type[t]['FP'] for t in types])
total_fn = sum([recall_per_type[t]['FN'] for t in types])

overall_precision = total_tp / (total_tp + total_fp) if total_tp + total_fp > 0 else 0
overall_recall = total_tp / (total_tp + total_fn) if total_tp + total_fn > 0 else 0

print(f'Overall: Precision = {overall_precision:.2f}, Recall = {overall_recall:.2f}')