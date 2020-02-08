import pandas as pd
labels = pd.read_csv('label_names.csv',sep=",")
data = pd.read_csv('solution_115.csv')
a = data.LabelConfidencePairs

i = 0
for item in a:

    print(data.VideoId[i])
    name_of_class = ''
    s = item.split()
    if s[0] == '342' and float(s[1]) > 0.99995:
        print(labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]])
        name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]]
    elif s[0] == '342' and float(s[1]) > 0.997:
        if float(s[3]) > 0.01 and s[2] != '0' and s[2] !='1':
            print(labels.label_name[labels.label_id[labels.label_id == int(s[2])].index[0]])
            name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[2])].index[0]]
        elif float(s[3]) > 0.1:
            print(labels.label_name[labels.label_id[labels.label_id == int(s[2])].index[0]])
            name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[2])].index[0]]
        else:
            print(labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]])
            name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]]
    elif s[0] == '342' and float(s[1]) < 0.997:
        # if s[2] != '0' and s[2] != '1':
        #     print(labels.label_name[labels.label_id[labels.label_id == int(s[2])].index[0]])
        #     name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[2])].index[0]]
        # else:
        #     print(labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]])
        #     name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]]
        name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[2])].index[0]]
    else:
        print(labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]])
        name_of_class = labels.label_name[labels.label_id[labels.label_id == int(s[0])].index[0]]
    if name_of_class != 'News program':
        data.LabelConfidencePairs[i] = 'Entertainment'
    else:
        data.LabelConfidencePairs[i] = name_of_class
    i+=1

data.to_csv('solution_115_final.csv',index=False)

    
    

