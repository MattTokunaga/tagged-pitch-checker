import pandas as pd
import sys
file = sys.argv[1]
print(file)
stats = ['RelSpeed', 'SpinRate', 'SpinAxis', 'VertBreak', 'InducedVertBreak', 'HorzBreak']
grouped = pd.read_csv("grouped.csv")
stat_conv = {
    'VELOCITY': 'RelSpeed',
    'SPIN RATE': 'SpinRate',
    'VERT BREAK': 'VertBreak',
    'HORZ BREAK': 'HorzBreak',
    'SPIN AXIS': 'SpinAxis'
}

def find_z_scores(pitcher, stat, val, z_dic):
    output = []
    temp = grouped[grouped.get("Pitcher") == pitcher]
    mean_col = stat + "_x"
    sd_col = stat + "_y"
    for pitch in temp.get("TaggedPitchType"):
        z_score = (val - temp[temp.get("TaggedPitchType") == pitch].get(mean_col).iloc[0]) / temp[temp.get("TaggedPitchType") == pitch].get(sd_col).iloc[0]
        output += [z_score]
        z_dic[pitch] += [z_score]
    return output

def find_all_z_scores(pitcher, stat_dic):
    #print(pitcher)
    for key in stat_dic.keys():
        stat_dic[key] = float(stat_dic[key])
    z_dic = {}
    temp = grouped[grouped.get("Pitcher") == pitcher]
    for pitch in temp.get("TaggedPitchType"):
        z_dic[pitch] = []
    for stat in stat_dic.keys():
        val = stat_dic[stat]
        stat = stat_conv[stat]
        find_z_scores(pitcher, stat, val, z_dic)
    return z_dic

#test_input_dic = {'VELOCITY': '94', 'SPIN RATE': '2211', 'VERT BREAK': '-15', 'HORZ BREAK': '15', 'SPIN AXIS': '224'}

def sum_z_scores(scores_dic):
    #print(scores_dic)
    output = {}
    for key in scores_dic.keys():
        squared_sum = 0
        for val in scores_dic[key]:
            squared_sum += val**2
        output[key] = squared_sum
    return output

#print(find_all_z_scores("Ryan Forucci", test_input_dic))

def predict_from_sums(summed_dic):
    output = ['', 0, '', 0]
    #print(summed_dic)
    min_sum = min(summed_dic.values())
    #print(summed_dic)
    for key in summed_dic:
        if summed_dic[key] == min_sum:
            output[0] = key
            output[1] = min_sum
            key1 = key
    del summed_dic[key1]
    if len(summed_dic.keys()) > 0:
        min_sum = min(summed_dic.values())
        for key in summed_dic:
            if summed_dic[key] == min_sum:
                output[2] = key 
                output[3] = min_sum
    return output

        
def predict(pitcher, input_dic):
    pred = predict_from_sums(sum_z_scores(find_all_z_scores(pitcher, input_dic)))
    #print(pred)
    return "Prediction: " + pred[0] + "; difference: " + str(pred[3] - pred[1])

def predict_from_csv(file):
    predict_list = []
    df = pd.read_csv(file)
    df = df.get(['Pitcher', 'PitchNo', 'TaggedPitchType', 'RelSpeed', 'SpinRate', 'VertBreak', 'HorzBreak', 'SpinAxis', 'PitcherTeam'])
    df = df[df.get('PitcherTeam') == df.get('PitcherTeam').iloc[0]]
    df = df.dropna()
    df = df.reset_index().reset_index()  
    for i in range(df.shape[0]):
        #print(df.get('Pitcher').iloc[i])
        stat_dic = {}
        stat_dic['VELOCITY'] = df.get('RelSpeed').iloc[i]
        stat_dic['SPIN RATE'] = df.get('SpinRate').iloc[i]
        stat_dic['VERT BREAK'] = df.get('VertBreak').iloc[i]
        stat_dic['HORZ BREAK'] = df.get('HorzBreak').iloc[i]
        stat_dic['SPIN AXIS'] = df.get('SpinAxis').iloc[i]
        prediction = predict(df.get('Pitcher').iloc[i], stat_dic)
        predict_list += [prediction[12:]]
    df = df.assign(pitch_pred = df.get('level_0').apply(lambda x: predict_list[x]))
    return df

def print_predicts():
    with_predict = predict_from_csv(file)
    for i in range(with_predict.shape[0]):
        if with_predict.get('TaggedPitchType').iloc[i] not in with_predict.get('pitch_pred').iloc[i]:
            print(str(with_predict.get('PitchNo').iloc[i]) + ", " + with_predict.get('pitch_pred').iloc[i])


print_predicts()