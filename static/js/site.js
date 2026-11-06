/* BURO travel. Progressive enhancement; content remains readable without JavaScript. */
(() => {
 'use strict';
 const init = () => {
  const $=(selector,root=document)=>root.querySelector(selector);
  const $$=(selector,root=document)=>Array.from(root.querySelectorAll(selector));
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  const header=$('.header'),menu=$('.mobile-menu'),modal=$('.modal'),menuButton=$('.menu-toggle');
  const updateHeader=()=>header?.classList.toggle('scrolled',window.scrollY>48);
  window.addEventListener('scroll',updateHeader,{passive:true});updateHeader();
  let overlay=null,previousFocus=null;
  const focusable=root=>$$('a[href],button:not([disabled]),input:not([type="hidden"]),select,textarea,[tabindex="0"]',root).filter(el=>el.getClientRects().length&&!el.closest('[hidden]'));
  const backgroundInert=enabled=>$$('body > header,body > main,body > footer').forEach(el=>el.inert=enabled);
  const closeOverlay=(restore=true)=>{
   if(!overlay)return;
   const current=overlay;overlay=null;
   current.classList.remove('open');current.setAttribute('aria-hidden','true');current.inert=true;
   document.body.classList.remove('overlay-open');backgroundInert(false);menuButton?.setAttribute('aria-expanded','false');
   if(restore&&previousFocus?.isConnected)previousFocus.focus({preventScroll:true});
  };
  const openOverlay=(element,trigger)=>{
   if(!element)return;
   if(overlay)closeOverlay(false);
   previousFocus=trigger||document.activeElement;overlay=element;
   element.inert=false;element.setAttribute('aria-hidden','false');element.classList.add('open');
   document.body.classList.add('overlay-open');backgroundInert(true);
   if(element===menu)menuButton?.setAttribute('aria-expanded','true');
   requestAnimationFrame(()=>{const first=element===modal?$('input[name="name"]',element):$('.close-mobile',element);(first||focusable(element)[0])?.focus({preventScroll:true});});
  };
  $$('[data-menu]').forEach(button=>button.addEventListener('click',()=>overlay===menu?closeOverlay():openOverlay(menu,button)));
  $$('.mobile-menu a').forEach(link=>link.addEventListener('click',()=>closeOverlay(false)));
  window.matchMedia('(min-width:1281px)').addEventListener('change',event=>{if(event.matches&&overlay===menu)closeOverlay();});
  $$('[data-open-form]').forEach(button=>button.addEventListener('click',event=>{
   event.preventDefault();
   const form=$('form',modal);
   if(form){
    const selected=$('[name="format"]',form);if(button.dataset.format&&selected)selected.value=button.dataset.format;
    const context=$('[name="program"]',form);if(context)context.value=button.dataset.program||'';
    const status=$('.form-status',form);if(status){status.hidden=true;status.textContent='';}
   }
   openOverlay(modal,button);
  }));
  $$('[data-close-form]').forEach(button=>button.addEventListener('click',()=>closeOverlay()));
  document.addEventListener('keydown',event=>{
   if(!overlay)return;
   if(event.key==='Escape'){event.preventDefault();closeOverlay();return;}
   if(event.key!=='Tab')return;
   const nodes=focusable(overlay),first=nodes[0],last=nodes.at(-1);
   if(!first){event.preventDefault();return;}
   if(event.shiftKey&&(document.activeElement===first||!overlay.contains(document.activeElement))){event.preventDefault();last.focus();}
   else if(!event.shiftKey&&(document.activeElement===last||!overlay.contains(document.activeElement))){event.preventDefault();first.focus();}
  });
  // Route atlas: buttons and SVG nodes share selection, photograph and caption.
  $$('[data-atlas]').forEach(atlas=>{
   const items=$$('[data-route]',atlas),image=$('[data-atlas-img]',atlas),caption=$('[data-atlas-cap]',atlas),preview=$('.atlas-preview',atlas);
   const choose=source=>{
    const id=source.dataset.route,title=source.dataset.title;
    items.forEach(item=>{
     const keys=(item.dataset.routes||item.dataset.route).split(' '),active=keys.includes(id);
     item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));
    });
    if(image&&source.dataset.image){image.removeAttribute('srcset');image.src=source.dataset.image;image.alt=title;}
    if(caption)caption.textContent=title;
    if(preview)preview.setAttribute('aria-label','Программы путешествий: '+title);
    atlas.dataset.selectedRoute=id;
   };
   items.forEach(item=>{
    item.addEventListener('click',()=>choose(item));
    if(item.tagName.toLowerCase()!=='button')item.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();choose(item);}});
   });
   atlas.dataset.selectedRoute='vlad';
  });
  $$('[data-carousel]').forEach(carousel=>{
   const rail=$('.rail',carousel),prev=$('[data-prev]',carousel),next=$('[data-next]',carousel);if(!rail)return;
   rail.setAttribute('aria-label','Популярные маршруты');
   const update=()=>{if(prev)prev.disabled=rail.scrollLeft<=2;if(next)next.disabled=rail.scrollLeft+rail.clientWidth>=rail.scrollWidth-3;};
   const move=direction=>rail.scrollBy({left:direction*rail.clientWidth*.8,behavior:reduced.matches?'instant':'smooth'});
   prev?.addEventListener('click',()=>move(-1));next?.addEventListener('click',()=>move(1));rail.addEventListener('scroll',update,{passive:true});
   if('ResizeObserver'in window)new ResizeObserver(update).observe(rail);else window.addEventListener('resize',update,{passive:true});
   update();
  });
  $$('[data-tabs]').forEach(group=>{
   const tabs=$$('.tab',group),panels=$$('.tab-panel',group);
   const choose=tab=>{
    tabs.forEach(item=>{const active=item===tab;item.classList.toggle('active',active);item.setAttribute('aria-selected',String(active));item.tabIndex=active?0:-1;});
    panels.forEach(panel=>panel.classList.toggle('active',panel.id===tab.dataset.target));
   };
   tabs.forEach((tab,index)=>{
    tab.addEventListener('click',()=>choose(tab));
    tab.addEventListener('keydown',event=>{
     let next;if(event.key==='ArrowRight')next=tabs[(index+1)%tabs.length];else if(event.key==='ArrowLeft')next=tabs[(index-1+tabs.length)%tabs.length];else if(event.key==='Home')next=tabs[0];else if(event.key==='End')next=tabs.at(-1);
     if(next){event.preventDefault();choose(next);next.focus();}
    });
   });
  });
  const filters=$$('[data-filter]'),programs=$$('.program-card[data-categories]'),grid=$('.filter-grid');
  filters.forEach(filter=>filter.addEventListener('click',()=>{
   filters.forEach(item=>{item.classList.toggle('active',item===filter);item.setAttribute('aria-pressed',String(item===filter));});
   let count=0;programs.forEach(card=>{const show=filter.dataset.filter==='all'||card.dataset.categories.split(' ').includes(filter.dataset.filter);card.hidden=!show;if(show)count++;});
   if(grid)grid.dataset.visibleCount=String(count);
  }));
  // Django forms: CSRF, server validation and explicit confirmation after DB save.
  $$('form[data-django-form]').forEach(form=>{
   const phone=$('[name="phone"]',form),name=$('[name="name"]',form);
   const validate=()=>{
    if(phone){const digits=phone.value.replace(/\D/g,'');phone.setCustomValidity(digits.length>=7&&digits.length<=15?'':'Укажите телефон с кодом города или страны.');}
    if(name)name.setCustomValidity(name.value.trim().length?'':'Укажите Ваше имя.');
   };
   phone?.addEventListener('input',()=>phone.setCustomValidity(''));name?.addEventListener('input',()=>name.setCustomValidity(''));
   form.addEventListener('submit',async event=>{
    event.preventDefault();validate();if(!form.reportValidity())return;
    const button=$('button[type="submit"]',form),status=$('.form-status',form);if(!button||button.disabled)return;
    const original=button.innerHTML;button.disabled=true;button.textContent='Отправляем…';form.setAttribute('aria-busy','true');
    if(status){status.hidden=true;status.textContent='';}
    const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),20000);
    let errorText='Не удалось отправить запрос. Данные сохранены в форме — попробуйте ещё раз или позвоните: +7 (928) 938-40-04.';
    try{
     const body=new URLSearchParams();for(const [key,value] of new FormData(form))body.append(key,String(value));
     const response=await fetch(form.action,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json','X-CSRFToken':$('[name="csrfmiddlewaretoken"]',form)?.value||''},body:body.toString(),signal:controller.signal});
     const result=await response.json();
     if(!response.ok||result.ok!==true){
      const errors=result.errors?Object.values(result.errors).flat():[];
      errorText=[result.message,...errors].filter(Boolean).join(' ')||errorText;
      throw new Error('Request rejected');
     }
     if(typeof result.redirect_url!=='string'||!result.redirect_url.startsWith('/'))throw new Error('Missing redirect');
     const destination=new URL(result.redirect_url,window.location.origin);
     if(destination.origin!==window.location.origin)throw new Error('Invalid redirect');
     window.location.assign(destination.href);
    }catch(error){
     if(status){status.textContent=errorText;status.hidden=false;}
     button.disabled=false;button.innerHTML=original;
    }finally{clearTimeout(timeout);form.removeAttribute('aria-busy');}
   });
  });
  // The content is visible by default, including when JS or IntersectionObserver is unavailable.
  if('IntersectionObserver'in window&&!reduced.matches){
   const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('in');observer.unobserve(entry.target);}}),{threshold:0,rootMargin:'0px 0px 30px 0px'});
   $$('.reveal').forEach(element=>{element.classList.add('will-reveal');observer.observe(element);});
  }
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
