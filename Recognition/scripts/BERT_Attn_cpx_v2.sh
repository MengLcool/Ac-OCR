exp_name='BERT_Attn_cpx_v2'
train_data='ictc_rd_small_400k-ver_enhance_819_500k-rd_cpx_200k-collect_img-ic_40_correct-tianchi_140k-LSVT-Synth_coco1-Synth_v1-ctwReCTS_train-gen_an_ch_name_250k-gen_ch_name_1000k'
train_ratio='0.05-0.05-0.05-0.05-0.15-0.15-0.2-0.05-0.05-0.1-0.1-0.1'
valid_data='/ai/local/menglc/v4_dataset/validate'

CUDA_VISIBLE_DEVICES=4 nohup \
python3 -u train.py \
 --experiment_name ${exp_name} \
 --Transformation TPS --FeatureExtraction SEResNet --SequenceModeling BERT --Prediction Attn \
 --num_fiducial 20 \
 --input_channel 1 \
 --output_channel 512 \
 --hidden_size 256 \
 --adam --lr 0.001 \
 --train_data /ai/local/menglc/v4_dataset/train \
 --valid_data ${valid_data} \
 --select_data  ${train_data}\
 --valInterval 500 \
 --batch_ratio ${train_ratio}\
 --manualSeed 2222 \
 --PAD \
 --batch_size 128 \
 --batch_max_length 35 \
 --imgH 32 --imgW 256 \
 --minC 10000 \
 --character cn_v4.txt \
 --my_model 0 \
 --continue_model saved_models/${exp_name}/best_norm_ED.pth \
 --grad_clip 10 \
>>log/${exp_name}.log

