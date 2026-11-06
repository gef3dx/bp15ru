// Execute the DELIVERED site.js in a minimal DOM fixture. No Django or real network.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const script=fs.readFileSync(require('path').join(__dirname,'..','static','js','site.js'),'utf8');
function fixture(server,values={}){
 const fields={name:'Проверка',phone:'+7 (900) 123-45-67',email:'a@example.test','form-name':'trip-request','source-page':'/',consent:'yes','submission-token':'signed-test',csrfmiddlewaretoken:'masked-csrf',...values};
 const nodes={};for(const[k,v]of Object.entries(fields))nodes[k]={value:v,addEventListener(){},setCustomValidity(message){this.validation=message;}};
 const status={hidden:true,textContent:''},button={disabled:false,innerHTML:'Отправить запрос',textContent:''},listeners={};
 const form={action:'https://buro.example/inquiries/submit/',fields,
  querySelector(s){if(s==='.form-status')return status;if(s==='button[type="submit"]')return button;const m=s.match(/\[name="([^"]+)"\]/);return m?nodes[m[1]]:null;},
  addEventListener(k,fn){listeners[k]=fn;},reportValidity(){return !Object.values(nodes).some(n=>n.validation);},setAttribute(){},removeAttribute(){}};
 const document={readyState:'complete',querySelector(){return null},querySelectorAll(s){return s==='form[data-django-form]'?[form]:[];},addEventListener(){}};
 let dest=null,calls=[];
 const sandbox={document,window:{location:{origin:'https://buro.example',assign(v){dest=v;}},matchMedia(){return{matches:true,addEventListener(){}}},addEventListener(){}},
  URL,URLSearchParams,AbortController,setTimeout,clearTimeout,FormData:class{constructor(f){this.f=f;}*[Symbol.iterator](){yield*Object.entries(this.f.fields)}},fetch:async(url,options)=>{calls.push({url,options});return server(url,options);}};
 vm.runInNewContext(script,sandbox);
 return{async submit(){await listeners.submit({preventDefault(){}})},form,fields,status,button,nodes,get calls(){return calls},get destination(){return dest}};
}
const ok=async()=>({ok:true,json:async()=>({ok:true,redirect_url:'/success.html'})});
(async()=>{
 const results=[];
 let f=fixture(ok);await f.submit();assert.equal(f.destination,'https://buro.example/success.html');assert.equal(f.calls[0].url,f.form.action);assert.equal(f.calls[0].options.headers['X-CSRFToken'],'masked-csrf');assert.equal(f.calls[0].options.headers.Accept,'application/json');assert.equal(new URLSearchParams(f.calls[0].options.body).get('form-name'),'trip-request');results.push('Success: endpoint + CSRF header + encoded fields + same-origin redirect PASS');
 for(const name of ['trip-request','contact-request']){f=fixture(ok,{'form-name':name});await f.submit();assert.equal(new URLSearchParams(f.calls[0].options.body).get('form-name'),name)}results.push('Both form names PASS');
 f=fixture(async()=>({ok:false,json:async()=>({ok:false,message:'Ошибка проверки',errors:{email:['Проверьте e-mail']}})}));await f.submit();assert.equal(f.destination,null);assert(!f.status.hidden);assert(f.status.textContent.includes('Проверьте e-mail'));assert.equal(f.fields.name,'Проверка');assert(!f.button.disabled);results.push('HTTP error: shows validation, preserves fields, re-enables button PASS');
 f=fixture(async()=>{throw Error('network')});await f.submit();assert.equal(f.destination,null);assert(!f.button.disabled);assert(!f.status.hidden);results.push('Network failure: no success redirect PASS');
 f=fixture(async()=>({ok:true,json:async()=>{throw Error('non-JSON response')}}));await f.submit();assert.equal(f.destination,null);assert(!f.button.disabled);results.push('Invalid server response rejected PASS');
 f=fixture(async()=>({ok:true,json:async()=>({ok:false})}));await f.submit();assert.equal(f.destination,null);results.push('HTTP 200 without explicit ok rejected PASS');
 f=fixture(async()=>({ok:true,json:async()=>({ok:true,redirect_url:'https://other.example'})}));await f.submit();assert.equal(f.destination,null);results.push('External redirect rejected PASS');
 f=fixture(ok,{phone:'abc'});await f.submit();assert.equal(f.calls.length,0);results.push('Client-side phone validation PASS');
 f=fixture(ok);f.button.disabled=true;await f.submit();assert.equal(f.calls.length,0);results.push('Duplicate click blocked PASS');
 console.log(results.join('\n'));
})().catch(e=>{console.error(e);process.exit(1)});
