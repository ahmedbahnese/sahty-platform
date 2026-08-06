"""
توليد صفحة HTML كاملة للملخص السريري التجريبي.
"""
import json, sys

with open('/tmp/demo_summary.json', encoding='utf-8') as f:
    s = json.load(f)

p   = s['patient']
dis = s['diseases']
sur = s['surgeries']
alg = s['allergies']
med = s['current_medications']
lab = s['lab_tests']
rad = s['radiology']
vis = s['visits']

# helpers
def age(dob):
    if not dob: return '—'
    from datetime import date
    b = date.fromisoformat(dob)
    t = date.today()
    a = t.year - b.year - ((t.month, t.day) < (b.month, b.day))
    return f"{a} سنة"

def fmt(iso):
    if not iso: return '—'
    from datetime import datetime
    try:
        d = datetime.fromisoformat(iso)
        months = ['يناير','فبراير','مارس','أبريل','مايو','يونيو',
                  'يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
        return f"{d.day} {months[d.month-1]} {d.year}"
    except:
        return iso

STATUS_LABEL = {'active':'نشط','chronic':'مزمن','resolved':'شُفي'}
STATUS_COLOR = {'active':'#3b82f6','chronic':'#8b5cf6','resolved':'#22c55e'}
SEV_LABEL = {'mild':'خفيف','moderate':'متوسط','severe':'شديد'}
SEV_COLOR = {'mild':'#f59e0b','moderate':'#f97316','severe':'#ef4444'}
LAB_LABEL = {'normal':'طبيعي','abnormal':'غير طبيعي','critical':'حرج'}
LAB_COLOR = {'normal':'#22c55e','abnormal':'#f97316','critical':'#ef4444'}
SCAN_LABEL = {'xray':'أشعة X','mri':'رنين مغناطيسي','ct':'أشعة مقطعية',
              'ultrasound':'موجات صوتية','pet':'PET Scan'}

def badge(label, color, bg=None):
    bg = bg or color + '22'
    return f'<span style="background:{bg};color:{color};padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600">{label}</span>'

html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>الملخص السريري — {p['first_name']} {p['last_name']}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Tahoma, Arial, sans-serif; background: #f1f5f9; color: #1e293b; direction: rtl; }}
  .page {{ max-width: 960px; margin: 0 auto; padding: 24px 16px; }}

  /* Header */
  .hdr {{ background: linear-gradient(135deg, #0f2444 0%, #1d4ed8 100%);
          color: #fff; border-radius: 16px; padding: 28px 32px; margin-bottom: 20px;
          display: flex; justify-content: space-between; align-items: flex-start; }}
  .hdr-logo {{ font-size: 13px; opacity: .75; margin-bottom: 8px; }}
  .hdr-name {{ font-size: 26px; font-weight: 700; }}
  .hdr-sub  {{ font-size: 14px; opacity: .85; margin-top: 4px; }}
  .hdr-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; min-width: 300px; }}
  .hdr-field {{ background: rgba(255,255,255,.12); border-radius: 10px; padding: 10px 14px; }}
  .hdr-field-label {{ font-size: 11px; opacity: .75; }}
  .hdr-field-val   {{ font-size: 14px; font-weight: 600; margin-top: 2px; }}

  /* Alert banner */
  .alert {{ background: #fef2f2; border: 1.5px solid #fca5a5; border-radius: 12px;
            padding: 14px 18px; margin-bottom: 16px; display: flex; align-items: center; gap: 12px; }}
  .alert-icon {{ font-size: 20px; }}
  .alert-txt {{ font-size: 13px; color: #b91c1c; font-weight: 600; }}

  /* Section */
  .section {{ background: #fff; border-radius: 14px; margin-bottom: 16px;
              box-shadow: 0 1px 4px rgba(0,0,0,.07); overflow: hidden; }}
  .section-hdr {{ background: linear-gradient(90deg, #eff6ff 0%, #fff 100%);
                  border-bottom: 1px solid #e2e8f0; padding: 14px 20px;
                  display: flex; align-items: center; gap: 10px; }}
  .section-icon {{ width: 32px; height: 32px; background: #2563eb; border-radius: 8px;
                   display: flex; align-items: center; justify-content: center; color: #fff; font-size: 15px; }}
  .section-title {{ font-size: 15px; font-weight: 700; color: #1e293b; flex: 1; }}
  .section-count {{ background: #e2e8f0; color: #475569; font-size: 12px; font-weight: 600;
                    padding: 2px 10px; border-radius: 20px; }}
  .section-body {{ padding: 18px 20px; }}

  /* Table */
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: right; padding: 8px 10px; color: #64748b; font-weight: 600;
        border-bottom: 2px solid #f1f5f9; font-size: 12px; }}
  td {{ padding: 10px 10px; border-bottom: 1px solid #f8fafc; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f8fafc; }}

  .drug-name {{ font-weight: 600; color: #1e293b; }}
  .drug-generic {{ font-size: 11px; color: #94a3b8; }}

  /* Timeline card */
  .t-card {{ border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 12px; }}
  .t-card:last-child {{ margin-bottom: 0; }}
  .t-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }}
  .t-title {{ font-weight: 700; color: #1e293b; font-size: 14px; }}
  .t-sub   {{ font-size: 12px; color: #64748b; margin-top: 2px; }}
  .t-date  {{ font-size: 13px; color: #64748b; white-space: nowrap; margin-right: 12px; }}
  .t-grid  {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; }}
  .t-field-lbl {{ font-size: 11px; color: #94a3b8; }}
  .t-field-val {{ font-size: 13px; color: #334155; margin-top: 2px; }}
  .t-report {{ background: #f8fafc; border-radius: 8px; padding: 12px; margin-top: 10px;
               font-size: 13px; color: #334155; line-height: 1.6; }}
  .t-report-lbl {{ font-size: 11px; color: #94a3b8; margin-bottom: 4px; font-weight: 600; }}

  /* Visit card */
  .v-card {{ border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px;
             margin-bottom: 10px; display: flex; align-items: center; gap: 14px;
             transition: background .15s; cursor: default; }}
  .v-card:hover {{ background: #f0f9ff; border-color: #93c5fd; }}
  .v-avatar {{ width: 44px; height: 44px; background: #dbeafe; border-radius: 12px;
               display: flex; align-items: center; justify-content: center;
               font-size: 20px; flex-shrink: 0; }}
  .v-body {{ flex: 1; }}
  .v-doc  {{ font-weight: 700; color: #1e293b; font-size: 14px; }}
  .v-spec {{ font-size: 12px; color: #64748b; }}
  .v-reason {{ font-size: 12px; color: #94a3b8; margin-top: 4px; }}
  .v-date {{ font-size: 13px; color: #64748b; white-space: nowrap; }}

  /* Allergy grid */
  .alg-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .alg-card {{ border-radius: 12px; padding: 14px; }}
  .alg-name {{ font-weight: 700; font-size: 14px; color: #1e293b; }}
  .alg-reaction {{ font-size: 13px; color: #475569; margin-top: 6px; }}

  /* Footer */
  .footer {{ text-align: center; padding: 24px; color: #94a3b8; font-size: 12px; }}
  .footer strong {{ color: #64748b; }}

  .empty {{ text-align: center; padding: 32px; color: #cbd5e1; font-size: 13px; }}
</style>
</head>
<body>
<div class="page">

<!-- ═══════ HEADER ═══════ -->
<div class="hdr">
  <div>
    <div class="hdr-logo">🏥 منصة صحتك في أمان — Patient Clinical Summary</div>
    <div class="hdr-name">{p['first_name']} {p['last_name']}</div>
    <div class="hdr-sub">{'ذكر' if p['gender']=='male' else 'أنثى'} · {age(p.get('date_of_birth'))} · فصيلة الدم: {p.get('blood_type','—')}</div>
  </div>
  <div class="hdr-info">
    <div class="hdr-field">
      <div class="hdr-field-label">رقم الملف (MRN)</div>
      <div class="hdr-field-val">{p.get('national_id','—')}</div>
    </div>
    <div class="hdr-field">
      <div class="hdr-field-label">تاريخ الميلاد</div>
      <div class="hdr-field-val">{fmt(p.get('date_of_birth'))}</div>
    </div>
    <div class="hdr-field">
      <div class="hdr-field-label">رقم الجوال</div>
      <div class="hdr-field-val">{p.get('phone','—')}</div>
    </div>
    <div class="hdr-field">
      <div class="hdr-field-label">التأمين الصحي</div>
      <div class="hdr-field-val">{p.get('insurance_provider','—')}</div>
    </div>
  </div>
</div>

<!-- ALLERGY ALERT -->
{''.join(f"""<div class="alert">
  <div class="alert-icon">⚠️</div>
  <div class="alert-txt">تنبيه حساسية شديدة: {a['allergen']} — {a.get('reaction','')}</div>
</div>""" for a in alg if a.get('severity')=='severe')}

<!-- ═══════ 1. PAST MEDICAL HISTORY ═══════ -->
<div class="section">
  <div class="section-hdr">
    <div class="section-icon">🩺</div>
    <div class="section-title">التاريخ المرضي السابق</div>
    <div class="section-count">{len(dis)}</div>
  </div>
  <div class="section-body">
    <table>
      <thead><tr>
        <th>المرض / الحالة</th><th>كود ICD</th><th>تاريخ التشخيص</th>
        <th>الحالة</th><th>الطبيب المعالج</th><th>ملاحظات</th>
      </tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td style="font-weight:600">{d['name']}</td>
        <td style="color:#64748b">{d.get('icd_code') or '—'}</td>
        <td>{fmt(d.get('diagnosis_date'))}</td>
        <td>{badge(STATUS_LABEL.get(d.get('status',''),'—'), STATUS_COLOR.get(d.get('status',''),'#64748b'))}</td>
        <td>{d.get('treating_doctor') or '—'}</td>
        <td style="color:#64748b;font-size:12px">{d.get('treatment_summary') or d.get('notes') or '—'}</td>
      </tr>""" for d in dis)}
      </tbody>
    </table>
  </div>
</div>

<!-- ═══════ 2. SURGICAL HISTORY ═══════ -->
<div class="section">
  <div class="section-hdr">
    <div class="section-icon">🔪</div>
    <div class="section-title">التاريخ الجراحي السابق</div>
    <div class="section-count">{len(sur)}</div>
  </div>
  <div class="section-body">
  {''.join(f"""<div class="t-card">
    <div class="t-header">
      <div>
        <div class="t-title">{s['name']}</div>
        <div class="t-sub">{s.get('surgery_type') or ''}</div>
      </div>
      <div class="t-date">📅 {fmt(s.get('surgery_date'))}</div>
    </div>
    <div class="t-grid">
      <div><div class="t-field-lbl">المستشفى</div><div class="t-field-val">{s.get('hospital') or '—'}</div></div>
      <div><div class="t-field-lbl">الجراح</div><div class="t-field-val">{s.get('surgeon') or '—'}</div></div>
      <div><div class="t-field-lbl">نوع التخدير</div><div class="t-field-val">{'عامة' if s.get('anesthesia_type')=='general' else 'نخاعي' if s.get('anesthesia_type')=='spinal' else s.get('anesthesia_type') or '—'}</div></div>
      <div><div class="t-field-lbl">مدة العملية</div><div class="t-field-val">{str(s.get('duration_minutes') or '—') + ' دقيقة' if s.get('duration_minutes') else '—'}</div></div>
      <div><div class="t-field-lbl">النتيجة</div><div class="t-field-val">{'ناجحة ✓' if s.get('outcome')=='successful' else s.get('outcome') or '—'}</div></div>
      <div><div class="t-field-lbl">موعد المتابعة</div><div class="t-field-val">{fmt(s.get('follow_up_date'))}</div></div>
    </div>
    {f'<div class="t-report"><div class="t-report-lbl">ملاحظات ما بعد العملية</div>{s["post_op_notes"]}</div>' if s.get('post_op_notes') else ''}
    {f'<div class="t-report" style="background:#fef2f2"><div class="t-report-lbl">المضاعفات</div>{s["complications"]}</div>' if s.get('complications') else ''}
  </div>""" for s in sur)}
  </div>
</div>

<!-- ═══════ 3. ALLERGIES ═══════ -->
<div class="section">
  <div class="section-hdr">
    <div class="section-icon">⚠️</div>
    <div class="section-title">الحساسية</div>
    <div class="section-count">{len(alg)}</div>
  </div>
  <div class="section-body">
    <div class="alg-grid">
    {''.join(f"""<div class="alg-card" style="background:{'#fef2f2' if a.get('severity')=='severe' else '#fff7ed' if a.get('severity')=='moderate' else '#fefce8'};border:1.5px solid {'#fca5a5' if a.get('severity')=='severe' else '#fdba74' if a.get('severity')=='moderate' else '#fde047'}">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div class="alg-name">{a['allergen']}</div>
        {badge(SEV_LABEL.get(a.get('severity',''),'—'), SEV_COLOR.get(a.get('severity',''),'#64748b')) if a.get('severity') else ''}
      </div>
      {f'<div class="alg-reaction"><strong>التفاعل:</strong> {a["reaction"]}</div>' if a.get('reaction') else ''}
      {f'<div style="font-size:12px;color:#94a3b8;margin-top:4px">{a["notes"]}</div>' if a.get('notes') else ''}
    </div>""" for a in alg)}
    </div>
  </div>
</div>

<!-- ═══════ 4. CURRENT MEDICATIONS ═══════ -->
<div class="section">
  <div class="section-hdr">
    <div class="section-icon">💊</div>
    <div class="section-title">الأدوية الحالية</div>
    <div class="section-count">{len(med)}</div>
  </div>
  <div class="section-body">
    <table>
      <thead><tr>
        <th>الدواء</th><th>الجرعة</th><th>الشكل</th><th>التكرار</th>
        <th>تاريخ البداية</th><th>تعليمات</th>
      </tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td><div class="drug-name">{m['name']}</div><div class="drug-generic">{m.get('generic_name') or ''}</div></td>
        <td style="font-weight:600;color:#2563eb">{m.get('dosage') or '—'}</td>
        <td style="color:#64748b">{m.get('form') or '—'}</td>
        <td>{m.get('frequency') or '—'}</td>
        <td>{fmt(m.get('start_date'))}</td>
        <td style="color:#64748b;font-size:12px">{m.get('instructions') or '—'}</td>
      </tr>""" for m in med)}
      </tbody>
    </table>
  </div>
</div>

<!-- ═══════ 5. LAB RESULTS ═══════ -->
<div class="section">
  <div class="section-hdr">
    <div class="section-icon">🧪</div>
    <div class="section-title">نتائج التحاليل المخبرية</div>
    <div class="section-count">{len(lab)}</div>
  </div>
  <div class="section-body">
    <table>
      <thead><tr>
        <th>اسم التحليل</th><th>الفئة</th><th>التاريخ</th>
        <th>النتيجة</th><th>المرجع</th><th>الحالة</th><th>الطبيب الطالب</th>
      </tr></thead>
      <tbody>
      {''.join(f"""<tr>
        <td style="font-weight:600">{l['test_name']}</td>
        <td style="color:#64748b;font-size:12px">{l.get('test_category') or '—'}</td>
        <td>{fmt(l.get('test_date'))}</td>
        <td style="font-weight:700;color:{'#ef4444' if l.get('status') in ('abnormal','critical') else '#16a34a'}">{l.get('result_value') or '—'} <span style="font-weight:400;color:#94a3b8;font-size:11px">{l.get('unit') or ''}</span></td>
        <td style="color:#64748b;font-size:12px">{l.get('reference_range') or '—'}</td>
        <td>{badge(LAB_LABEL.get(l.get('status',''),'—'), LAB_COLOR.get(l.get('status',''),'#64748b'))}</td>
        <td style="color:#64748b;font-size:12px">{l.get('ordering_doctor') or '—'}</td>
      </tr>""" for l in lab)}
      </tbody>
    </table>
  </div>
</div>

<!-- ═══════ 6. RADIOLOGY ═══════ -->
<div class="section">
  <div class="section-hdr">
    <div class="section-icon">🔬</div>
    <div class="section-title">الأشعة والتصوير الطبي</div>
    <div class="section-count">{len(rad)}</div>
  </div>
  <div class="section-body">
  {''.join(f"""<div class="t-card">
    <div class="t-header">
      <div>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="background:#e0f2fe;color:#0369a1;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">{SCAN_LABEL.get(r.get('scan_type',''),'—')}</span>
          <span style="font-weight:700;font-size:14px">{r.get('body_part') or ''}</span>
        </div>
        <div class="t-sub">{r.get('facility') or ''}</div>
      </div>
      <div class="t-date">📅 {fmt(r.get('scan_date'))}</div>
    </div>
    <div class="t-grid" style="grid-template-columns:1fr 1fr">
      <div><div class="t-field-lbl">الأخصائي</div><div class="t-field-val">{r.get('radiologist') or '—'}</div></div>
      <div><div class="t-field-lbl">الطبيب الطالب</div><div class="t-field-val">{r.get('ordering_doctor') or '—'}</div></div>
    </div>
    {f'<div class="t-report"><div class="t-report-lbl">📋 النتائج</div>{r["findings"]}</div>' if r.get('findings') else ''}
    {f'<div class="t-report" style="background:#f0fdf4;border:1px solid #bbf7d0"><div class="t-report-lbl">✅ الانطباع</div>{r["impression"]}</div>' if r.get('impression') else ''}
    {f'<div class="t-report" style="background:#fffbeb"><div class="t-report-lbl">💡 التوصية</div>{r["recommendation"]}</div>' if r.get('recommendation') else ''}
  </div>""" for r in rad)}
  </div>
</div>

<!-- ═══════ 7. DOCTOR VISITS ═══════ -->
<div class="section">
  <div class="section-hdr">
    <div class="section-icon">🩻</div>
    <div class="section-title">زيارات الطبيب</div>
    <div class="section-count">{len(vis)}</div>
  </div>
  <div class="section-body">
  {''.join(f"""<div class="v-card">
    <div class="v-avatar">🩺</div>
    <div class="v-body">
      <div class="v-doc">{v.get('doctor',{}).get('name','—') if v.get('doctor') else '—'}</div>
      <div class="v-spec">{v.get('doctor',{}).get('specialization','') if v.get('doctor') else ''}</div>
      <div class="v-reason">{v.get('reason') or ''}</div>
    </div>
    <div>
      <div class="v-date">📅 {fmt(v.get('appointment_date'))}</div>
      <div style="margin-top:4px">{badge('مكتملة','#16a34a')}</div>
    </div>
  </div>""" for v in vis)}
  </div>
</div>

<!-- FOOTER -->
<div class="footer">
  <strong>منصة صحتك في أمان</strong> — تقرير سريري موثّق إلكترونياً<br>
  تاريخ الطباعة: {fmt(str(__import__('datetime').date.today()))} &nbsp;|&nbsp; جميع البيانات سرية وخاصة بالمريض
</div>

</div>
</body>
</html>"""

out = '/home/runner/workspace/dist/demo-clinical-summary.html'
import os; os.makedirs('/home/runner/workspace/dist', exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Written to {out}')
