// Cole no Apps Script. O destinatário é fixo, definido pelo administrador.
const DESTINATARIO = 'wanderson.silva@etapa.com.br';
function resposta_(dados) {
  return ContentService.createTextOutput(JSON.stringify(dados))
    .setMimeType(ContentService.MimeType.JSON);
}
function autorizarEmail() {
  // Execute uma vez no editor para conceder permissão, sem enviar e-mail.
  console.log('Cota disponível: ' + MailApp.getRemainingDailyQuota());
}
function doPost(e) {
  const secreto = PropertiesService.getScriptProperties().getProperty('BBANK_MAIL_TOKEN');
  if (!secreto || secreto.length < 32) return resposta_({ok: false, code: 'config'});
  let dados;
  try { dados = JSON.parse(e.postData.contents); }
  catch (_) { return resposta_({ok: false, code: 'invalid'}); }
  if (dados.token !== secreto) return resposta_({ok: false, code: 'auth'});
  if (typeof dados.subject !== 'string' || !dados.subject.startsWith('BBank — Solicitação de aquisição — ')
      || dados.subject.length > 200 || /[\r\n]/.test(dados.subject)
      || typeof dados.body !== 'string' || dados.body.length > 5000
      || typeof dados.requestId !== 'string' || !/^[a-f0-9]{32}$/.test(dados.requestId)) {
    return resposta_({ok: false, code: 'invalid'});
  }
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return resposta_({ok: false, code: 'busy'});
  try {
    const cache = CacheService.getScriptCache();
    const id = 'sent:' + dados.requestId;
    if (cache.get(id)) return resposta_({ok: true});
    if (MailApp.getRemainingDailyQuota() < 1) return resposta_({ok: false, code: 'quota'});
    MailApp.sendEmail({to: DESTINATARIO, subject: dados.subject, body: dados.body, name: 'BBank 2026'});
    cache.put(id, '1', 21600);
    return resposta_({ok: true});
  } catch (erro) {
    console.error('Falha no envio: ' + erro.message);
    return resposta_({ok: false, code: 'send'});
  } finally { lock.releaseLock(); }
}
