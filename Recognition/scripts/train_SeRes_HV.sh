CUDA_VISIBLE_DEVICES=5,6 nohup \
python3 -u train.py \
 --experiment_name train_SERes_HV \
 --Transformation TPS --FeatureExtraction SEResNet --SequenceModeling BiLSTM --Prediction Attn \
 --num_fiducial 20 \
 --input_channel 1 \
 --output_channel 512 \
 --hidden_size 256 \
 --adam --lr 0.001 \
 --train_data /ai/local/menglc/v3_dataset/train \
 --valid_data /ai/local/menglc/v3_dataset/validate \
 --select_data  ic_40_correct-tianchi_140k-ictc_rd_small_400k-v2_4100k-v2_700k-ver_enhance_819_500k\
 --valInterval 2000 \
 --batch_ratio 0.1-0.25-0.15-0.1-0.2-0.2 \
 --manualSeed 2222 \
 --PAD \
 --batch_size 192 \
 --batch_max_length 35 \
 --imgH 32 --imgW 256 \
 --minC 4000 \
 --character cn_bigger.txt \
 --continue_model saved_models/train_SERes_HV/best_norm_ED.pth \
>>result_HV_SEResNet.log

