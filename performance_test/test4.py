import os, time, warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import cv2
import numpy as np
import mediapipe as mp
from tensorflow import keras
from sklearn.metrics import (confusion_matrix, classification_report,
                              roc_auc_score, roc_curve, accuracy_score,
                              precision_score, recall_score, f1_score)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

LSTM_MODEL_PATH  = 'best_acc_final.keras'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIOLENT_DIR = os.path.join(BASE_DIR, 'violence-detection-dataset', 'violent')
NON_VIOLENT_DIR = os.path.join(BASE_DIR, 'violence-detection-dataset', 'non-violent')
SEQUENCE_LEN     = 63
NUM_FEATURES     = 72
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mkv', '.mov', '.wmv')

mp_pose = mp.solutions.pose

def extract_keypoints_from_video(video_path, seq_len=SEQUENCE_LEN, num_feat=NUM_FEATURES):
    cap = cv2.VideoCapture(video_path)
    frames_kp = []

    with mp_pose.Pose(static_image_mode=False,
                      model_complexity=1,
                      min_detection_confidence=0.3,
                      min_tracking_confidence=0.3) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                kp = []
                for lm in results.pose_landmarks.landmark:
                    kp.extend([lm.x, lm.y])
                kp = kp[:num_feat]
                kp += [0.0] * (num_feat - len(kp))
            else:
                kp = [0.0] * num_feat

            frames_kp.append(kp)
    cap.release()

    if len(frames_kp) == 0:
        return None

    frames_kp = np.array(frames_kp, dtype=np.float32)

    if len(frames_kp) >= seq_len:
        frames_kp = frames_kp[:seq_len]
    else:
        pad = np.tile(frames_kp[-1], (seq_len - len(frames_kp), 1))
        frames_kp = np.vstack([frames_kp, pad])

    return frames_kp


def collect_videos(folder):
    videos = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(VIDEO_EXTENSIONS):
                videos.append(os.path.join(root, f))
    return sorted(videos)


print("\n  Loading LSTM model ...")
lstm_model = keras.models.load_model(LSTM_MODEL_PATH)
print("  Model loaded successfully!\n")

violent_videos     = collect_videos(VIOLENT_DIR)
non_violent_videos = collect_videos(NON_VIOLENT_DIR)
print("\nFirst violent video:")
print(violent_videos[0])

print("\nFirst non-violent video:")
print(non_violent_videos[0])

print(f"  Violent videos     : {len(violent_videos)}")
print(f"  Non-violent videos : {len(non_violent_videos)}\n")

if len(violent_videos) == 0 and len(non_violent_videos) == 0:
    print("  WARNING: No video files found!")
    print(f"  Check paths:\n    {VIOLENT_DIR}\n    {NON_VIOLENT_DIR}")
    exit()

all_videos  = violent_videos + non_violent_videos
true_labels = [1] * len(violent_videos) + [0] * len(non_violent_videos)

y_true, y_pred, y_score = [], [], []
times   = []
skipped = 0
total   = len(all_videos)

for i, (vpath, label) in enumerate(zip(all_videos, true_labels)):
    name = os.path.basename(vpath)
    print(f"  [{i+1}/{total}] {name} ...", end=' ')

    t0  = time.time()
    seq = extract_keypoints_from_video(vpath)

    if seq is None:
        print("Skipped (extraction failed)")
        skipped += 1
        continue

    X_input = seq[np.newaxis, ...]
    prob = lstm_model.predict(X_input, verbose=0)[0]

    print("Probabilities:", prob)

    elapsed = (time.time() - t0) * 1000

    pred  = int(np.argmax(prob))
    score = float(prob[1])
    

    y_true.append(label)
    y_pred.append(pred)
    y_score.append(score)
    times.append(elapsed)

    status = "OK" if pred == label else "WRONG"
    print(f"{status}  (score={score:.3f}, {elapsed:.0f}ms)")

print(f"\n  Done: {len(y_true)} videos | Skipped: {skipped}\n")

if len(y_true) == 0:
    print("  No results to display.")
    exit()

y_true  = np.array(y_true)
y_pred  = np.array(y_pred)
y_score = np.array(y_score)

acc      = accuracy_score(y_true, y_pred)
prec     = precision_score(y_true, y_pred, zero_division=0)
rec      = recall_score(y_true, y_pred, zero_division=0)
f1       = f1_score(y_true, y_pred, zero_division=0)
auc      = roc_auc_score(y_true, y_score) if len(np.unique(y_true)) > 1 else 0.0
cm       = confusion_matrix(y_true, y_pred)
fpr, tpr, _ = roc_curve(y_true, y_score) if len(np.unique(y_true)) > 1 else ([0,1],[0,1],None)
avg_time = np.mean(times)

print("=" * 50)
print(f"  Accuracy  : {acc*100:.2f}%")
print(f"  Precision : {prec*100:.2f}%")
print(f"  Recall    : {rec*100:.2f}%")
print(f"  F1 Score  : {f1*100:.2f}%")
print(f"  AUC-ROC   : {auc*100:.2f}%")
print(f"  Inference : {avg_time:.0f} ms/video")
print("=" * 50)
print()
print(classification_report(y_true, y_pred,
      target_names=['Non-Violence', 'Violence'], zero_division=0))

fig = plt.figure(figsize=(20, 10))
fig.patch.set_facecolor('#0f172a')
fig.suptitle('Realtime Violence Detection System — Video Evaluation',
             fontsize=16, fontweight='bold', color='white', y=0.98)
gs = gridspec.GridSpec(2, 4, figure=fig, wspace=0.42, hspace=0.55)

def style_ax(ax, title):
    ax.set_facecolor('#1e293b')
    ax.set_title(title, color='white', fontsize=11, fontweight='bold', pad=10)
    ax.tick_params(colors='#94a3b8')
    for sp in ax.spines.values():
        sp.set_edgecolor('#334155')

ax1 = fig.add_subplot(gs[0, 0])
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1,
            xticklabels=['Non-Violence', 'Violence'],
            yticklabels=['Non-Violence', 'Violence'],
            annot_kws={'color': 'white', 'size': 13})
style_ax(ax1, 'Confusion Matrix')
ax1.set_ylabel('True Label', color='#94a3b8', fontsize=9)
ax1.set_xlabel('Predicted',  color='#94a3b8', fontsize=9)
ax1.set_xticklabels(['Non-V', 'Violence'], color='#94a3b8', fontsize=8)
ax1.set_yticklabels(['Non-V', 'Violence'], color='#94a3b8', fontsize=8)

ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(fpr, tpr, color='#60a5fa', lw=2.5, label=f'AUC = {auc:.4f}')
ax2.plot([0,1],[0,1],'--',color='#475569',lw=1)
ax2.fill_between(fpr, tpr, alpha=0.15, color='#60a5fa')
style_ax(ax2, 'ROC Curve')
ax2.set_xlabel('False Positive Rate', color='#94a3b8', fontsize=9)
ax2.set_ylabel('True Positive Rate',  color='#94a3b8', fontsize=9)
ax2.legend(loc='lower right', facecolor='#1e293b', labelcolor='white', fontsize=10)
ax2.set_xlim([0,1]); ax2.set_ylim([0,1.02])

ax3 = fig.add_subplot(gs[0, 2])
m_names = ['Accuracy','Precision','Recall','F1 Score','AUC-ROC']
m_vals  = [acc, prec, rec, f1, auc]
colors  = ['#60a5fa','#34d399','#f59e0b','#f87171','#a78bfa']
bars = ax3.bar(m_names, m_vals, color=colors, width=0.55, edgecolor='#0f172a')
for bar, val in zip(bars, m_vals):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
             f'{val:.3f}', ha='center', va='bottom',
             fontsize=9, fontweight='bold', color='white')
ax3.set_ylim([0,1.15])
style_ax(ax3, 'Performance Metrics')
ax3.set_ylabel('Score', color='#94a3b8', fontsize=9)
ax3.tick_params(axis='x', rotation=20)

ax4 = fig.add_subplot(gs[0, 3])
txt = (f"Model: LSTM + MediaPipe\n\n"
       f"Total Videos:   {len(y_true)}\n"
       f"  Violent:      {int(y_true.sum())}\n"
       f"  Non-Violent:  {int((y_true==0).sum())}\n"
       f"Skipped:        {skipped}\n\n"
       f"Accuracy:  {acc*100:.2f}%\n"
       f"Precision: {prec*100:.2f}%\n"
       f"Recall:    {rec*100:.2f}%\n"
       f"F1 Score:  {f1*100:.2f}%\n"
       f"AUC-ROC:   {auc*100:.2f}%\n\n"
       f"Inference: {avg_time:.0f} ms/video")
ax4.text(0.08, 0.95, txt, transform=ax4.transAxes, fontsize=9.5,
         color='#e2e8f0', va='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#0f172a', alpha=0.8))
style_ax(ax4, 'Summary')
ax4.set_xticks([]); ax4.set_yticks([])

ax5 = fig.add_subplot(gs[1, 0])
correct   = int((np.array(y_pred) == y_true).sum())
incorrect = len(y_true) - correct
ax5.pie([correct, incorrect],
        labels=[f'Correct\n({correct})', f'Wrong\n({incorrect})'],
        colors=['#34d399','#f87171'],
        autopct='%1.1f%%', startangle=90)
for t in ax5.texts:
    t.set_color('white'); t.set_fontsize(10)
style_ax(ax5, 'Prediction Results')

ax6 = fig.add_subplot(gs[1, 1])
ax6.hist(y_score[y_true==1], bins=15, color='#f87171',
         alpha=0.75, label='Violent', edgecolor='#0f172a')
ax6.hist(y_score[y_true==0], bins=15, color='#34d399',
         alpha=0.75, label='Non-Violent', edgecolor='#0f172a')
ax6.axvline(x=0.5, color='white', linestyle='--', lw=1.5, label='Threshold=0.5')
style_ax(ax6, 'Score Distribution')
ax6.set_xlabel('Violence Score', color='#94a3b8', fontsize=9)
ax6.set_ylabel('Count',          color='#94a3b8', fontsize=9)
ax6.legend(facecolor='#1e293b', labelcolor='white', fontsize=9)

ax7 = fig.add_subplot(gs[1, 2])
ax7.hist(times, bins=15, color='#60a5fa', edgecolor='#0f172a', alpha=0.85)
ax7.axvline(x=avg_time, color='#f59e0b', linestyle='--',
            lw=2, label=f'Mean={avg_time:.0f}ms')
style_ax(ax7, 'Inference Time per Video')
ax7.set_xlabel('Time (ms)', color='#94a3b8', fontsize=9)
ax7.set_ylabel('Count',     color='#94a3b8', fontsize=9)
ax7.legend(facecolor='#1e293b', labelcolor='white', fontsize=9)

ax8 = fig.add_subplot(gs[1, 3])
tp = int(((y_pred==1)&(y_true==1)).sum())
tn = int(((y_pred==0)&(y_true==0)).sum())
fp = int(((y_pred==1)&(y_true==0)).sum())
fn = int(((y_pred==0)&(y_true==1)).sum())
txt2 = (f"Confusion Details\n\n"
        f"TP (Violence correct):   {tp}\n"
        f"TN (Non-V correct):      {tn}\n"
        f"FP (False alarm):        {fp}\n"
        f"FN (Missed violence):    {fn}\n\n"
        f"Sequence Length: {SEQUENCE_LEN} frames\n"
        f"Features/frame:  {NUM_FEATURES}\n"
        f"Keypoints Tool:  MediaPipe\n\n"
        f"Avg Inference:   {avg_time:.0f} ms/video")
ax8.text(0.08, 0.95, txt2, transform=ax8.transAxes, fontsize=9.5,
         color='#e2e8f0', va='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#0f172a', alpha=0.8))
style_ax(ax8, 'Detailed Results')
ax8.set_xticks([]); ax8.set_yticks([])

output_path = 'metrics_evaluation_videos.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
print(f"\n  Chart saved: {output_path}")