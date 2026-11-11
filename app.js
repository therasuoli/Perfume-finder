const $=id=>document.getElementById(id);
let perfumes=[],favorites=JSON.parse(localStorage.getItem('pf_favs')||'[]'),onlyFav=false,quickTerm='',deferred;
const faGender=g=>({women:'زنانه',men:'مردانه',unisex:'یونیسکس'})[String(g||'').toLowerCase()]||'ثبت نشده';
const faCountry=c=>({'UAE':'امارات','United Arab Emirates':'امارات','France':'فرانسه','FR':'فرانسه'})[c]||c||'نامشخص';
const faNum=n=>new Intl.NumberFormat('fa-IR').format(n);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const arr=x=>Array.isArray(x)?x:(typeof x==='string'?x.split(/[,،|;]/).map(s=>s.trim()).filter(Boolean):[]);
const allNotes=p=>[...arr(p.top),...arr(p.heart),...arr(p.base),...arr(p.notes)].join(' ');
const textOf=p=>[p.name,p.brand,p.country,p.family,p.description,p.character,allNotes(p),...arr(p.tags),...arr(p.seasons)].join(' ').toLowerCase();
function toast(s){$('toast').textContent=s;$('toast').style.display='block';clearTimeout(window._toast);window._toast=setTimeout(()=>$('toast').style.display='none',2400)}
function normalize(p,i){
 const top=arr(p.top||p.top_notes),heart=arr(p.heart||p.middle||p.heart_notes),base=arr(p.base||p.base_notes);
 let tags=[...arr(p.tags),...arr(p.seasons),...arr(p.times_of_day)];
 return {...p,id:String(p.id||`perfume-${i}`),name:p.name||p.title||'بدون نام',brand:p.brand||p.house||'برند نامشخص',country:faCountry(p.country||p.country_of_origin),gender:String(p.gender||'').toLowerCase(),family:p.family||p.primary_family||p.secondary_family||'ثبت نشده',top,heart,base,tags,description:p.description||p.character||'توضیحات تکمیلی این عطر در منبع داده ثبت نشده است.',url:p.url||'',verified:p.verified||'catalog'};
}
function fillSelect(id,values,first){let el=$(id),old=el.value;let v=[...new Set(values.filter(x=>x&&x!=='نامشخص'&&x!=='ثبت نشده'))].sort((a,b)=>a.localeCompare(b,'fa'));el.innerHTML=`<option value="">${first}</option>`+v.map(x=>`<option value="${esc(x)}">${esc(x)}</option>`).join('');el.value=v.includes(old)?old:''}
function setupOptions(){fillSelect('country',perfumes.map(p=>p.country),'همه کشورها');fillSelect('brand',perfumes.map(p=>p.brand),'همه برندها');fillSelect('family',perfumes.map(p=>p.family),'همه خانواده‌ها')}
function warmScore(p){let t=textOf(p);if(/خنک|تازه|مرکبات|آبی|دریایی|سبز|بهار|تابستان/.test(t))return 20;if(/گرم|شرقی|ادویه|وانیل|عنبر|عود|چرم|زمستان|پاییز/.test(t))return 80;return 50}
function sliderFilter(p){let n=+$('scentSlider').value;if(n<12||n>88)return true;let s=warmScore(p);return Math.abs(s-n)<=42}
function smartQuery(q){q=q.toLowerCase().trim();const synonyms={'oud':'عود','agarwood':'عود','rose':'رز','vanilla':'وانیل','fresh':'خنک','freshie':'خنک','citrus':'مرکبات','woody':'چوبی','sweet':'شیرین','amber':'عنبر','musk':'مشک','leather':'چرم','floral':'گلی','spicy':'ادویه‌ای','summer':'تابستان','winter':'زمستان','spring':'بهار','autumn':'پاییز','uae':'امارات','dubai':'امارات','french':'فرانسه','france':'فرانسه'};for(const [a,b] of Object.entries(synonyms))q=q.replaceAll(a,b);return q}
function render(){
 let q=smartQuery(($('search').value+' '+quickTerm).trim()),note=smartQuery($('note').value.trim());
 let arrp=perfumes.filter(p=>{
  if(onlyFav&&!favorites.includes(p.id))return false;
  if($('country').value&&p.country!==$('country').value)return false;
  if($('brand').value&&p.brand!==$('brand').value)return false;
  if($('gender').value&&p.gender!==$('gender').value)return false;
  if($('family').value&&p.family!==$('family').value)return false;
  if($('season').value&&!textOf(p).includes($('season').value))return false;
  if(note&&!smartQuery(allNotes(p)).includes(note))return false;
  if(q&&!textOf(p).includes(q))return false;
  if(!sliderFilter(p))return false;
  return true;
 });
 if($('sort').value==='az')arrp.sort((a,b)=>a.name.localeCompare(b.name));
 if($('sort').value==='brand')arrp.sort((a,b)=>a.brand.localeCompare(b.brand));
 $('count').textContent=faNum(perfumes.length);$('resultCount').textContent=faNum(arrp.length)+' نتیجه';
 $('resultTitle').textContent=onlyFav?'علاقه‌مندی‌های من':'کاتالوگ عطرها';
 $('cards').innerHTML=arrp.length?arrp.map(p=>`<article class="card" data-id="${esc(p.id)}"><div class="cardtop"><span class="country">${esc(p.country||'بین‌المللی')}</span><button class="heart ${favorites.includes(p.id)?'on':''}" data-fav="${esc(p.id)}">${favorites.includes(p.id)?'♥':'♡'}</button></div><div class="bottle"></div><h3>${esc(p.name)}</h3><div class="maker">${esc(p.brand)}</div><div class="tags"><span class="tag gender">${faGender(p.gender)}</span><span class="tag">${esc(p.family)}</span>${arr(p.tags).slice(0,1).map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><div class="notes"><b>نت‌ها:</b> ${esc([...p.top,...p.heart,...p.base].slice(0,5).join('، ')||'در انتظار تکمیل')}</div><div class="desc">${esc(p.description)}</div></article>`).join(''):'<div class="empty">عطری با این مشخصات پیدا نشد. فیلترها یا عبارت جست‌وجو را تغییر بده.</div>';
}
function similarity(a,b){
 const aa=[...a.top,...a.heart,...a.base].map(x=>x.toLowerCase()),bb=[...b.top,...b.heart,...b.base].map(x=>x.toLowerCase());
 let A=new Set(aa),B=new Set(bb),inter=[...A].filter(x=>B.has(x)).length,union=new Set([...A,...B]).size;
 let noteScore=union?inter/union:0,fam=a.family&&a.family===b.family?.2:0,tagA=new Set(a.tags),tagB=new Set(b.tags),tagScore=[...tagA].filter(x=>tagB.has(x)).length/Math.max(1,new Set([...tagA,...tagB]).size);
 return noteScore*.72+fam+tagScore*.08;
}
function similarFor(p){
 let from=$('fromCountry').value, target=p.country==='فرانسه'?'امارات':p.country==='امارات'?'فرانسه':'';
 let wanted=from||target;
 let list=perfumes.filter(x=>x.id!==p.id&&(!wanted||x.country===wanted)).map(x=>({p:x,s:similarity(p,x)})).sort((a,b)=>b.s-a.s);
 return list.slice(0,4);
}
function detail(id){
 let p=perfumes.find(x=>x.id===id);if(!p)return;
 $('dname').textContent=p.name;$('dbrand').textContent=p.brand+' · '+(p.country||'کشور نامشخص');
 $('dmeta').innerHTML=[`<span class="tag gender">${faGender(p.gender)}</span>`,`<span class="tag">${esc(p.family)}</span>`,...arr(p.tags).slice(0,5).map(x=>`<span class="tag">${esc(x)}</span>`)].join('');
 const groups=[['نت‌های آغازین',p.top],['نت‌های میانی',p.heart],['نت‌های پایه',p.base]];
 $('pyramid').innerHTML=groups.map(([title,notes])=>`<div><b>${title}</b><p>${notes.length?notes.map(esc).join('، '):'اطلاعات ثبت نشده'}</p></div>`).join('');
 $('ddesc').textContent=p.description||'توضیحات ثبت نشده است.';
 const sims=similarFor(p);let wanted=$('fromCountry').value||(p.country==='فرانسه'?'امارات':p.country==='امارات'?'فرانسه':'');
 $('similarTitle').textContent=wanted?`پیشنهاد از کشور ${wanted} بر اساس اشتراک نت‌ها`:'پیشنهاد بر اساس اشتراک نت‌ها و خانواده بویایی';
 $('similarList').innerHTML=sims.length?sims.map(({p:x,s})=>`<button class="similar" data-sim="${esc(x.id)}"><b>${esc(x.name)}</b><small>${esc(x.brand)} · ${esc(x.country)} · شباهت ${Math.round(s*100)}٪</small></button>`).join(''):'<div class="empty">برای پیشنهاد مشابه از کشور مقابل، به داده‌های بیشتری نیاز داریم.</div>';
 $('dsource').textContent=(p.verified==='curated'?'رکورد منتخب نمونه؛ جزئیات تجاری را با منبع رسمی تطبیق دهید.':'منبع داده: '+(p.source||'کاتالوگ محلی'))+(p.url?' · '+p.url:'');
 $('modal').classList.add('show');
}
function reset(){['search','note','country','brand','gender','family','season','fromCountry'].forEach(id=>$(id).value='');$('sort').value='default';$('scentSlider').value=50;$('sliderValue').textContent='متعادل';quickTerm='';document.querySelectorAll('.chip').forEach((b,i)=>b.classList.toggle('active',i===0));onlyFav=false;$('favView').textContent='♡ علاقه‌مندی‌ها';render()}
async function init(){
 const r=await fetch('data.json');const raw=await r.json();perfumes=raw.map(normalize);setupOptions();render();
 $('cards').addEventListener('click',e=>{let f=e.target.closest('[data-fav]');if(f){let id=f.dataset.fav;favorites=favorites.includes(id)?favorites.filter(x=>x!==id):[...favorites,id];localStorage.setItem('pf_favs',JSON.stringify(favorites));render();return}let c=e.target.closest('[data-id]');if(c)detail(c.dataset.id)});
 $('similarList').addEventListener('click',e=>{let b=e.target.closest('[data-sim]');if(b)detail(b.dataset.sim)});
 ['country','brand','gender','family','season','sort','fromCountry','note'].forEach(id=>$(id).addEventListener('input',render));
 $('search').addEventListener('input',render);$('searchBtn').onclick=()=>{render();toast('جست‌وجوی هوشمند در کاتالوگ انجام شد.')};
 $('search').addEventListener('keydown',e=>{if(e.key==='Enter'){$('searchBtn').click()}});
 $('quick').addEventListener('click',e=>{let b=e.target.closest('[data-q]');if(!b)return;document.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));b.classList.add('active');quickTerm=b.dataset.q;render()});
 $('scentSlider').addEventListener('input',()=>{let n=+$('scentSlider').value;$('sliderValue').textContent=n<30?'خنک':n>70?'گرم':'متعادل';render()});
 $('resetBtn').onclick=reset;$('favView').onclick=()=>{onlyFav=!onlyFav;$('favView').textContent=onlyFav?'نمایش همه':'♡ علاقه‌مندی‌ها';render()};
 $('close').onclick=()=>$('modal').classList.remove('show');$('modal').onclick=e=>{if(e.target===$('modal'))$('modal').classList.remove('show')};
}
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferred=e;$('installBtn').hidden=false});
$('installBtn').onclick=async()=>{if(deferred){deferred.prompt();deferred=null}else toast('از منوی مرورگر گزینه نصب برنامه یا افزودن به صفحه اصلی را انتخاب کن.')};
init().catch(()=>toast('خطا در بارگذاری کاتالوگ؛ فایل data.json را بررسی کن.'));
if('serviceWorker'in navigator&&location.protocol.startsWith('http'))navigator.serviceWorker.register('./sw.js').catch(()=>{});
