import './_group.css';
import { AppLayout } from './_shared/AppLayout';
import { useEffect, useState } from 'react';
import {
  Activity, AlertTriangle, ArrowUpRight, CalendarDays, Check, ChevronRight,
  Clock3, Droplets, HeartPulse, MapPin, MessageCircle, Pill, ShieldCheck,
  Stethoscope, TestTube2, Video, X, Zap,
} from 'lucide-react';
import {
  CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';

const bpData = [
  { day: 'السبت', systolic: 118, diastolic: 77 },
  { day: 'الأحد', systolic: 122, diastolic: 80 },
  { day: 'الإثنين', systolic: 119, diastolic: 78 },
  { day: 'الثلاثاء', systolic: 121, diastolic: 79 },
  { day: 'الأربعاء', systolic: 117, diastolic: 76 },
  { day: 'الخميس', systolic: 120, diastolic: 80 },
  { day: 'اليوم', systolic: 120, diastolic: 80 },
];

const appointments = [
  { name: 'د. سارة الحسن', specialty: 'طب القلب والأوعية', date: 'غداً، 12 يونيو', time: '10:30 صباحاً', hospital: 'مستشفى مدينة الشيخ شخبوط', type: 'In-person', status: 'Confirmed' },
  { name: 'د. خالد المنصوري', specialty: 'الطب الباطني', date: 'الأحد، 15 يونيو', time: '04:00 مساءً', hospital: 'عيادات كليفلاند أبوظبي', type: 'Video', status: 'Confirmed' },
  { name: 'د. ليلى ناصر', specialty: 'طب العيون', date: 'الخميس، 19 يونيو', time: '09:15 صباحاً', hospital: 'مركز النور الطبي', type: 'In-person', status: 'Pending' },
];

const labs = [
  { title: 'تحليل الدم الشامل', en: 'CBC', date: '10 يونيو 2024', status: 'Normal', color: 'var(--sahti-success)', values: 'WBC 6.4 · Hgb 14.2 · PLT 248' },
  { title: 'تحليل الدهون', en: 'Lipid Panel', date: '08 يونيو 2024', status: 'High', color: 'var(--sahti-warning)', values: 'LDL 142 · HDL 56 · TG 118' },
];

function StatCard({ icon: Icon, label, value, detail, tone = 'teal', action }: { icon: typeof Activity; label: string; value: string; detail: string; tone?: string; action?: boolean }) {
  return <div className="patient-stat" style={{ borderTop: `3px solid var(--sahti-${tone})` }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div className={`stat-icon ${tone}`}><Icon size={18} /></div>
      {action && <span style={{ background: 'var(--sahti-warning-bg)', color: 'var(--sahti-warning)', fontSize: 10, fontWeight: 700, padding: '4px 7px', borderRadius: 20 }}>جديد</span>}
    </div>
    <div style={{ marginTop: 14, color: 'var(--sahti-text-muted)', fontSize: 11 }}>{label}</div>
    <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: '-.5px', marginTop: 4 }}>{value}</div>
    <div style={{ color: 'var(--sahti-text-secondary)', fontSize: 11, marginTop: 3 }}>{detail}</div>
  </div>;
}

export function PatientDashboard() {
  const [taken, setTaken] = useState<number[]>([]);
  const [seconds, setSeconds] = useState(42 * 60 + 18);
  const [showAssistant, setShowAssistant] = useState(false);
  useEffect(() => {
    const timer = window.setInterval(() => setSeconds((s) => s > 0 ? s - 1 : 0), 1000);
    return () => window.clearInterval(timer);
  }, []);
  const countdown = `${String(Math.floor(seconds / 3600)).padStart(2, '0')}:${String(Math.floor((seconds % 3600) / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;

  return <AppLayout role="patient">
    <style>{`
      .patient-page { max-width: 1500px; margin: 0 auto; animation: patientIn .5s ease both; }
      @keyframes patientIn { from { opacity: 0; transform: translateY(8px) } to { opacity: 1; transform: translateY(0) } }
      .patient-grid { display:grid; grid-template-columns: minmax(0,1.5fr) minmax(320px,1fr); gap:18px; }
      .patient-stat { background:var(--sahti-surface); border:1px solid var(--sahti-border); border-radius:14px; padding:16px; box-shadow:var(--shadow-card); min-width:0; }
      .stat-icon { width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center; }
      .stat-icon.teal { color:var(--sahti-teal-dark);background:var(--sahti-teal-pale) } .stat-icon.success { color:var(--sahti-success);background:var(--sahti-success-bg) } .stat-icon.warning { color:var(--sahti-warning);background:var(--sahti-warning-bg) } .stat-icon.info { color:var(--sahti-info);background:var(--sahti-info-bg) }
      .patient-card { background:var(--sahti-surface); border:1px solid var(--sahti-border); border-radius:14px; box-shadow:var(--shadow-card); overflow:hidden; }
      .section-head { display:flex; justify-content:space-between; align-items:center; padding:18px 20px 14px; }
      .section-title { font-size:15px; font-weight:800; color:var(--sahti-text-primary); }
      .section-sub { font-size:11px; color:var(--sahti-text-muted); margin-top:2px; }
      .outline-btn { border:1px solid var(--sahti-border); background:var(--sahti-surface); color:var(--sahti-teal-dark); border-radius:8px; padding:7px 10px; font:600 11px var(--font-body); cursor:pointer; }
      .appointment { display:flex; align-items:center; gap:12px; padding:14px 20px; border-top:1px solid var(--sahti-border); }
      .appt-date { width:48px; height:52px; border-radius:10px; background:var(--sahti-teal-pale); color:var(--sahti-teal-dark); display:flex; flex-direction:column; align-items:center; justify-content:center; flex-shrink:0; }
      .appt-date strong { font-size:18px; line-height:18px }.appt-date span { font-size:9px;font-weight:700 }
      .pill-btn { border:0; background:var(--sahti-teal); color:white; border-radius:8px; padding:8px 11px; font:700 10px var(--font-body); cursor:pointer; white-space:nowrap; }
      .pill-btn:hover { background:var(--sahti-teal-dark) }.muted-btn { background:var(--sahti-bg); color:var(--sahti-text-secondary); }
      .med-row { display:flex; align-items:center; gap:11px; padding:13px 20px; border-top:1px solid var(--sahti-border); }
      .med-icon { width:36px;height:36px;border-radius:10px;background:#EEF8F7;color:var(--sahti-success);display:flex;align-items:center;justify-content:center;flex-shrink:0; }
      .metric-grid { display:grid; grid-template-columns:1fr 1fr; border-top:1px solid var(--sahti-border); }
      .metric { padding:14px 18px; border-right:1px solid var(--sahti-border); border-bottom:1px solid var(--sahti-border) }.metric:nth-child(even){border-right:0}.metric:nth-last-child(-n+2){border-bottom:0}
      @media (max-width: 1050px) { .patient-grid { grid-template-columns:1fr } }
      @media (max-width: 720px) { .patient-grid { display:block }.patient-stat { margin-bottom:10px }.stats-grid { grid-template-columns:1fr 1fr !important }.appointment { align-items:flex-start; flex-wrap:wrap }.appointment > div:nth-child(2){flex:1;min-width:170px}.appointment .appointment-actions{width:100%;padding-left:60px}.welcome { flex-direction:column; align-items:flex-start !important; gap:12px !important } }
    `}</style>
    <div className="patient-page">
      <div className="welcome" style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:22 }}>
        <div><div style={{ color:'var(--sahti-text-muted)', fontSize:12, marginBottom:4 }}>الأربعاء، ١١ يونيو ٢٠٢٤ · أبوظبي</div><h1 style={{ fontFamily:'var(--font-display)', fontSize:27, letterSpacing:'-1px', margin:0 }}>صباح الخير، أحمد <span style={{ color:'var(--sahti-teal)' }}>✦</span></h1><p style={{ color:'var(--sahti-text-secondary)', marginTop:5, fontSize:12 }}>إليك ملخص صحتك لهذا اليوم. استمر في العناية بنفسك.</p></div>
        <div style={{ display:'flex', alignItems:'center', gap:9, padding:'10px 14px', background:'var(--sahti-success-bg)', border:'1px solid #BBF7D0', color:'var(--sahti-success)', borderRadius:12, fontSize:12, fontWeight:700 }}><ShieldCheck size={17}/> جميع المؤشرات طبيعية</div>
      </div>
      <div className="stats-grid" style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:20 }}>
        <StatCard icon={CalendarDays} label="الموعد القادم" value="غداً، 10:30" detail="د. سارة الحسن · قلب" />
        <StatCard icon={Pill} label="الأدوية الحالية" value="3 أدوية" detail="الجرعة القادمة بعد 42 دقيقة" tone="success" />
        <StatCard icon={TestTube2} label="نتائج المختبر" value="نتيجة واحدة" detail="تحليل الدهون متاح" tone="warning" action />
        <StatCard icon={MessageCircle} label="الإشعارات" value="2 غير مقروءة" detail="آخر تحديث منذ 18 دقيقة" tone="info" />
      </div>
      <div className="patient-grid">
        <div style={{ display:'flex', flexDirection:'column', gap:18 }}>
          <section className="patient-card"><div className="section-head"><div><div className="section-title">المواعيد القادمة</div><div className="section-sub">لا تفوّت موعدك القادم</div></div><button className="outline-btn">عرض الكل <ChevronRight size={12} style={{ verticalAlign:'middle' }}/></button></div>
            {appointments.map((a, i) => <div className="appointment" key={a.name}><div className="appt-date"><strong>{i === 0 ? '12' : i === 1 ? '15' : '19'}</strong><span>يونيو</span></div><div style={{ flex:1 }}><div style={{ fontSize:13, fontWeight:800 }}>{a.name}</div><div style={{ fontSize:11, color:'var(--sahti-text-secondary)', marginTop:3 }}>{a.specialty}</div><div style={{ fontSize:10, color:'var(--sahti-text-muted)', marginTop:5, display:'flex', gap:8, flexWrap:'wrap' }}><span><Clock3 size={11} style={{ verticalAlign:'middle' }}/> {a.time}</span><span><MapPin size={11} style={{ verticalAlign:'middle' }}/> {a.hospital}</span></div></div><div className="appointment-actions" style={{ display:'flex', flexDirection:'column', alignItems:'flex-end', gap:7 }}><span style={{ fontSize:9, fontWeight:700, padding:'4px 7px', borderRadius:20, background:a.status === 'Pending' ? 'var(--sahti-warning-bg)' : 'var(--sahti-success-bg)', color:a.status === 'Pending' ? 'var(--sahti-warning)' : 'var(--sahti-success)' }}>{a.status}</span><button className={`pill-btn ${a.type === 'In-person' ? 'muted-btn' : ''}`}>{a.type === 'Video' ? <><Video size={11} style={{verticalAlign:'middle'}}/> انضم للمكالمة</> : 'عرض التفاصيل'}</button></div></div>)}
          </section>
          <section className="patient-card"><div className="section-head"><div><div className="section-title">المؤشرات الحيوية</div><div className="section-sub">قراءاتك خلال آخر ٧ أيام</div></div><span style={{ fontSize:10, color:'var(--sahti-success)', fontWeight:700 }}><Activity size={12} style={{verticalAlign:'middle'}}/> مستقر</span></div><div style={{ height:175, padding:'0 14px 4px 0' }}><ResponsiveContainer width="100%" height="100%"><LineChart data={bpData}><CartesianGrid stroke="var(--sahti-border)" strokeDasharray="3 3" vertical={false}/><XAxis dataKey="day" tick={{ fontSize:9, fill:'var(--sahti-text-muted)' }} axisLine={false} tickLine={false}/><YAxis domain={[60,140]} tick={{ fontSize:9, fill:'var(--sahti-text-muted)' }} axisLine={false} tickLine={false} width={25}/><Tooltip contentStyle={{ borderRadius:8, border:'1px solid var(--sahti-border)', fontSize:11 }}/><Line type="monotone" dataKey="systolic" stroke="var(--sahti-teal)" strokeWidth={2.5} dot={{ r:3, fill:'var(--sahti-teal)' }} name="الانقباضي"/><Line type="monotone" dataKey="diastolic" stroke="var(--sahti-navy-60)" strokeWidth={2} strokeDasharray="4 3" dot={false} name="الانبساطي"/></LineChart></ResponsiveContainer></div><div className="metric-grid">{[{icon:HeartPulse,label:'ضغط الدم',value:'120/80',unit:'mmHg',tone:'teal'},{icon:Activity,label:'نبض القلب',value:'72',unit:'bpm',tone:'success'},{icon:Droplets,label:'سكر الدم',value:'95',unit:'mg/dL',tone:'warning'},{icon:Zap,label:'نسبة الأكسجين',value:'98',unit:'SpO2 %',tone:'info'}].map(({icon:Icon,label,value,unit,tone})=><div className="metric" key={label}><div style={{display:'flex',alignItems:'center',gap:7,color:`var(--sahti-${tone})`,fontSize:10}}><Icon size={14}/>{label}</div><div style={{fontSize:20,fontWeight:800,marginTop:6}}>{value} <small style={{fontSize:10,fontWeight:500,color:'var(--sahti-text-muted)'}}>{unit}</small></div></div>)}</div></section>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:18 }}>
          <section className="patient-card"><div className="section-head"><div><div className="section-title">الأدوية الحالية</div><div className="section-sub">تذكير الجرعات اليومية</div></div><button className="outline-btn">إدارة الأدوية</button></div>{[['Atorvastatin','20 mg · مرة يومياً'],['Metformin','500 mg · مرتان يومياً'],['Vitamin D3','1000 IU · مرة يومياً']].map(([name,dose],i)=><div className="med-row" key={name}><div className="med-icon"><Pill size={17}/></div><div style={{flex:1}}><div style={{fontWeight:800,fontSize:12}}>{name}</div><div style={{color:'var(--sahti-text-secondary)',fontSize:10,marginTop:3}}>{dose}</div></div>{taken.includes(i)?<span style={{fontSize:10,color:'var(--sahti-success)',fontWeight:700}}><Check size={13} style={{verticalAlign:'middle'}}/> تم أخذها</span>:<button onClick={()=>setTaken(t=>[...t,i])} className="pill-btn muted-btn">تأكيد الأخذ</button>}</div>)}<div style={{margin:'14px 20px 16px',padding:'10px 12px',background:'var(--sahti-bg)',borderRadius:9,display:'flex',alignItems:'center',gap:8,fontSize:11,color:'var(--sahti-text-secondary)'}}><Clock3 size={14} color="var(--sahti-teal)"/> الجرعة القادمة خلال <strong style={{color:'var(--sahti-navy)'}}>{countdown}</strong></div></section>
          <section className="patient-card"><div className="section-head"><div><div className="section-title">نتائج المختبر الأخيرة</div><div className="section-sub">تم تحديثها هذا الأسبوع</div></div><button className="outline-btn">كل النتائج</button></div>{labs.map(l=><div key={l.en} style={{padding:'13px 20px',borderTop:'1px solid var(--sahti-border)',display:'flex',alignItems:'center',gap:11}}><div style={{width:35,height:35,borderRadius:10,background:'var(--sahti-bg)',display:'flex',alignItems:'center',justifyContent:'center',color:l.color}}><TestTube2 size={16}/></div><div style={{flex:1}}><div style={{fontSize:12,fontWeight:800}}>{l.title} <span style={{fontSize:9,color:'var(--sahti-text-muted)',fontWeight:500}}>({l.en})</span></div><div style={{fontSize:10,color:'var(--sahti-text-secondary)',marginTop:3}}>{l.values}</div><div style={{fontSize:9,color:'var(--sahti-text-muted)',marginTop:3}}>{l.date}</div></div><span style={{fontSize:10,fontWeight:800,color:l.color,background:l.status==='High'?'var(--sahti-warning-bg)':'var(--sahti-success-bg)',padding:'5px 8px',borderRadius:20}}>{l.status}</span></div>)}</section>
          <section className="bg-mesh-navy" style={{borderRadius:14,padding:18,color:'white',position:'relative',overflow:'hidden'}}><div style={{position:'relative',zIndex:1}}><div style={{display:'flex',alignItems:'center',gap:8,fontSize:14,fontWeight:800}}><MessageCircle size={18} color="#7DD3FC"/> مساعد صحتي الذكي</div><p style={{fontSize:11,color:'rgba(255,255,255,.7)',margin:'8px 0 13px',lineHeight:1.7}}>اسأل عن أدويتك، أعراضك، أو نتائج تحاليلك.</p><button onClick={()=>setShowAssistant(v=>!v)} style={{border:0,borderRadius:8,padding:'8px 12px',background:'#0EA5E9',color:'white',font:'700 10px var(--font-body)',cursor:'pointer'}}>{showAssistant?'إغلاق المحادثة':'ابدأ محادثة'} <ArrowUpRight size={12} style={{verticalAlign:'middle'}}/></button></div><div style={{position:'absolute',right:-20,bottom:-30,width:120,height:120,borderRadius:'50%',border:'1px solid rgba(125,211,252,.2)'}}/></section>
        </div>
      </div>
      <section style={{marginTop:18,background:'var(--sahti-emergency-bg)',border:'1px solid #FECACA',borderRadius:14,padding:'14px 18px',display:'flex',alignItems:'center',gap:14,flexWrap:'wrap'}}><div style={{width:38,height:38,borderRadius:11,background:'var(--sahti-emergency)',color:'white',display:'flex',alignItems:'center',justifyContent:'center'}}><AlertTriangle size={20}/></div><div style={{flex:1,minWidth:220}}><div style={{fontWeight:800,fontSize:13,color:'#991B1B'}}>تحتاج إلى مساعدة عاجلة؟</div><div style={{fontSize:10,color:'#B45353',marginTop:3}}>تواصل سريعاً مع خدمات الطوارئ أو أفراد عائلتك</div></div><div style={{display:'flex',gap:8,alignItems:'center'}}><span style={{fontSize:10,color:'#991B1B',fontWeight:700}}>العائلة: +971 50 123 4567</span><button onClick={()=>window.alert('سيتم الاتصال بخدمات الطوارئ 998')} style={{background:'var(--sahti-emergency)',color:'white',border:0,borderRadius:8,padding:'9px 13px',font:'700 11px var(--font-body)',cursor:'pointer'}}>طوارئ 998</button></div></section>
    </div>
  </AppLayout>;
}