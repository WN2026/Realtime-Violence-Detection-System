import os, time, json
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 1) LSTM Evaluation
print("  Evaluating LSTM (best_acc_final.keras) ...")

import tf_keras as keras
from sklearn.metrics import (confusion_matrix, classification_report,
                              roc_auc_score, roc_curve, accuracy_score,
                              precision_score, recall_score, f1_score)

X = np.load('testx.npy', allow_pickle=True)
Y = np.load('testy.npy', allow_pickle=True)
lstm_model = keras.models.load_model('best_acc_final.keras')

t0 = time.time()
probs = lstm_model.predict(X, verbose=0)
lstm_time = (time.time() - t0) / X.shape[0] * 1000

y_true  = np.argmax(Y, axis=1)
y_pred  = np.argmax(probs, axis=1)
y_score = probs[:, 1]

L = {
    'acc':  accuracy_score(y_true, y_pred),
    'prec': precision_score(y_true, y_pred),
    'rec':  recall_score(y_true, y_pred),
    'f1':   f1_score(y_true, y_pred),
    'auc':  roc_auc_score(y_true, y_score),
    'cm':   confusion_matrix(y_true, y_pred).tolist(),
    'fpr':  roc_curve(y_true, y_score)[0].tolist(),
    'tpr':  roc_curve(y_true, y_score)[1].tolist(),
    'time': lstm_time,
    'n':    X.shape[0]
}

print(f"\n  Samples   : {L['n']}")
print(f"  Accuracy  : {L['acc']*100:.2f}%")
print(f"  Precision : {L['prec']*100:.2f}%")
print(f"  Recall    : {L['rec']*100:.2f}%")
print(f"  F1 Score  : {L['f1']*100:.2f}%")
print(f"  AUC-ROC   : {L['auc']*100:.2f}%")
print(f"  Inference : {L['time']:.2f} ms/sample")
print()
print(classification_report(y_true, y_pred,
      target_names=['Non-Violence', 'Violence']))

# 2) YOLOv8 Evaluation
print("  Evaluating YOLOv8 (yolov8n.pt) ...")

from ultralytics import YOLO

YOLO_MODEL_PATH  = '../yolov8n.pt'
IMAGES_DIR       = '../violence_images/'
WEAPON_CLASSES   = {'knife', 'gun', 'pistol', 'rifle', 'scissors'}
CONF_THRESHOLD   = 0.25

yolo_model = YOLO(YOLO_MODEL_PATH)
imgs = sorted(os.listdir(IMAGES_DIR))

y_pred_yolo, y_score_yolo, times = [], [], []

for img_name in imgs:
    img_path = os.path.join(IMAGES_DIR, img_name)
    t0 = time.time()
    results = yolo_model(img_path, verbose=False)
    times.append((time.time() - t0) * 1000)

    boxes = results[0].boxes
    names = results[0].names
    score = 0.0

    if boxes is not None:
        for cls, conf in zip(boxes.cls, boxes.conf):
            if names[int(cls)].lower() in WEAPON_CLASSES \
               and float(conf) >= CONF_THRESHOLD:
                score = max(score, float(conf))

    y_pred_yolo.append(1 if score > 0 else 0)
    y_score_yolo.append(score)

detected  = sum(y_pred_yolo)
missed    = len(imgs) - detected
avg_time  = np.mean(times)

Y_res = {
    'detected':  detected,
    'total':     len(imgs),
    'y_pred':    y_pred_yolo,
    'y_score':   y_score_yolo,
    'avg_time':  avg_time
}

print(f"\n  Test Images : {Y_res['total']}")
print(f"  Detected    : {detected}/{Y_res['total']}  ({detected/Y_res['total']*100:.2f}%)")
print(f"  Missed      : {missed}/{Y_res['total']}")
print(f"  Inference   : {avg_time:.1f} ms/image")

# 3) Plot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

lstm_cm = np.array(L['cm'])
fpr     = np.array(L['fpr'])
tpr     = np.array(L['tpr'])
conf_vals = [s for s in Y_res['y_score'] if s > 0.01]

fig = plt.figure(figsize=(20, 10))
fig.patch.set_facecolor('#0f172a')
fig.suptitle('Realtime Violence Detection System — Metrics Evaluation',
             fontsize=16, fontweight='bold', color='white', y=0.98)
gs = gridspec.GridSpec(2, 4, figure=fig, wspace=0.42, hspace=0.55)

def style_ax(ax, title):
    ax.set_facecolor('#1e293b')
    ax.set_title(title, color='white', fontsize=11, fontweight='bold', pad=10)
    ax.tick_params(colors='#94a3b8')
    for sp in ax.spines.values():
        sp.set_edgecolor('#334155')

# Row 1: LSTM
ax1 = fig.add_subplot(gs[0, 0])
sns.heatmap(lstm_cm, annot=True, fmt='d', cmap='Blues', ax=ax1,
            xticklabels=['Non-Violence', 'Violence'],
            yticklabels=['Non-Violence', 'Violence'],
            annot_kws={'color': 'white', 'size': 13})
style_ax(ax1, 'LSTM — Confusion Matrix')
ax1.set_ylabel('True Label', color='#94a3b8', fontsize=9)
ax1.set_xlabel('Predicted',  color='#94a3b8', fontsize=9)
ax1.set_xticklabels(['Non-Violence', 'Violence'], color='#94a3b8', fontsize=8)
ax1.set_yticklabels(['Non-Violence', 'Violence'], color='#94a3b8', fontsize=8)

ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(fpr, tpr, color='#60a5fa', lw=2.5, label=f'AUC = {L["auc"]:.4f}')
ax2.plot([0, 1], [0, 1], '--', color='#475569', lw=1)
ax2.fill_between(fpr, tpr, alpha=0.15, color='#60a5fa')
style_ax(ax2, 'LSTM — ROC Curve')
ax2.set_xlabel('False Positive Rate', color='#94a3b8', fontsize=9)
ax2.set_ylabel('True Positive Rate',  color='#94a3b8', fontsize=9)
ax2.legend(loc='lower right', facecolor='#1e293b', labelcolor='white', fontsize=10)
ax2.set_xlim([0, 1]); ax2.set_ylim([0, 1.02])

ax3 = fig.add_subplot(gs[0, 2])
m_names = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC-ROC']
m_vals  = [L['acc'], L['prec'], L['rec'], L['f1'], L['auc']]
colors  = ['#60a5fa', '#34d399', '#f59e0b', '#f87171', '#a78bfa']
bars = ax3.bar(m_names, m_vals, color=colors, width=0.55, edgecolor='#0f172a')
for bar, val in zip(bars, m_vals):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{val:.3f}', ha='center', va='bottom',
             fontsize=9, fontweight='bold', color='white')
ax3.set_ylim([0, 1.15])
style_ax(ax3, 'LSTM — Performance Metrics')
ax3.set_ylabel('Score', color='#94a3b8', fontsize=9)
ax3.tick_params(axis='x', rotation=20)

ax4 = fig.add_subplot(gs[0, 3])
txt = (f"Model: LSTM + OpenPose\n\n"
       f"Test Samples:   {L['n']}\n"
       f"Sequence:       63 frames\n"
       f"Features/frame: 72\n\n"
       f"Accuracy:  {L['acc']*100:.2f}%\n"
       f"Precision: {L['prec']*100:.2f}%\n"
       f"Recall:    {L['rec']*100:.2f}%\n"
       f"F1 Score:  {L['f1']*100:.2f}%\n"
       f"AUC-ROC:   {L['auc']*100:.2f}%\n\n"
       f"Inference: {L['time']:.2f} ms/sample")
ax4.text(0.08, 0.95, txt, transform=ax4.transAxes, fontsize=9.5,
         color='#e2e8f0', va='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#0f172a', alpha=0.8))
style_ax(ax4, 'LSTM — Summary')
ax4.set_xticks([]); ax4.set_yticks([])

# Row 2: YOLOv8
ax5 = fig.add_subplot(gs[1, 0])
wedges, texts, autotexts = ax5.pie(
    [detected, missed],
    labels=[f'Detected\n({detected})', f'Missed\n({missed})'],
    colors=['#34d399', '#f87171'],
    autopct='%1.1f%%', startangle=90)
for t in texts + autotexts:
    t.set_color('white'); t.set_fontsize(10)
style_ax(ax5, 'YOLOv8 — Detection Rate')

ax6 = fig.add_subplot(gs[1, 1])
ax6.hist(conf_vals, bins=15, color='#34d399', edgecolor='#0f172a', alpha=0.85)
ax6.axvline(x=CONF_THRESHOLD, color='#f87171', linestyle='--',
            lw=2, label=f'Threshold={CONF_THRESHOLD}')
style_ax(ax6, 'YOLOv8 — Confidence Distribution')
ax6.set_xlabel('Confidence Score', color='#94a3b8', fontsize=9)
ax6.set_ylabel('Count',            color='#94a3b8', fontsize=9)
ax6.legend(facecolor='#1e293b', labelcolor='white', fontsize=9)

ax7 = fig.add_subplot(gs[1, 2])
y_names  = ['Detection\nRate', 'Recall\n(Weapon)']
y_vals   = [detected / Y_res['total'], detected / Y_res['total']]
y_colors = ['#34d399', '#60a5fa']
bars2 = ax7.bar(y_names, y_vals, color=y_colors, width=0.45, edgecolor='#0f172a')
for bar, val in zip(bars2, y_vals):
    ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{val:.3f}', ha='center', va='bottom',
             fontsize=11, fontweight='bold', color='white')
ax7.set_ylim([0, 1.15])
style_ax(ax7, 'YOLOv8 — Performance Metrics')
ax7.set_ylabel('Score', color='#94a3b8', fontsize=9)

ax8 = fig.add_subplot(gs[1, 3])
txt2 = (f"Model: YOLOv8n (nano)\n\n"
        f"Test Images:    {Y_res['total']}\n"
        f"Weapon Classes: knife, gun\n"
        f"Conf Threshold: {CONF_THRESHOLD}\n\n"
        f"Detected:  {detected}/{Y_res['total']}\n"
        f"Missed:    {missed}/{Y_res['total']}\n"
        f"Det. Rate: {detected/Y_res['total']*100:.2f}%\n\n"
        f"Inference: {avg_time:.1f} ms/img")
ax8.text(0.08, 0.95, txt2, transform=ax8.transAxes, fontsize=9.5,
         color='#e2e8f0', va='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#0f172a', alpha=0.8))
style_ax(ax8, 'YOLOv8 — Summary')
ax8.set_xticks([]); ax8.set_yticks([])

output_path = 'metrics_evaluation_full.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0f172a')
print(f"\nChart saved: {output_path}")
