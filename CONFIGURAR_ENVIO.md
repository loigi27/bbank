# BBank: envio automático sem Brevo

A configuração abaixo é feita uma vez pelo administrador. Depois, o aluno clica em Solicitar e o Google envia o e-mail automaticamente. Não precisa instalar aplicativo de e-mail, fornecer telefone ao Brevo ou clicar em Enviar.

1. Abra https://script.google.com/ com a conta Google que enviará os e-mails e crie um Novo projeto.
2. Apague o código de exemplo e cole o conteúdo de Google_Email.gs. Salve.
3. Na engrenagem Configurações do projeto, em Propriedades do script, adicione BBANK_MAIL_TOKEN. Escolha um segredo aleatório de pelo menos 32 caracteres. Guarde-o; ele será colocado também no Render. Não publique o segredo no GitHub nem o compartilhe com os alunos.
4. Volte ao Editor, selecione a função autorizarEmail e clique em Executar. Autorize o acesso de envio de e-mail na conta escolhida. Essa função apenas consulta a cota; não envia um teste.
5. Clique em Implantar → Nova implantação → engrenagem → Aplicativo da Web. Selecione Executar como: Eu e Quem pode acessar: Qualquer pessoa. Implante e copie a URL que termina em /exec (não /dev).
6. No Render, abra seu serviço → Environment e adicione:
   - GOOGLE_MAIL_URL: a URL /exec copiada.
   - BBANK_MAIL_TOKEN: exatamente o mesmo segredo colocado nas propriedades do script.
7. Substitua o BBank.py do GitHub pelo deste pacote, mantendo esse nome. O Google_Email.gs não precisa ir para o GitHub; ele vai no editor do Google.
8. Salve as variáveis e faça um novo deploy. O comando de início pode continuar python BBank.py. Não precisa instalar bibliotecas adicionais.
9. Teste uma solicitação. A página só confirma o envio depois da resposta positiva do Google. Confira o e-mail recebido e a pasta de spam.

O destinatário permanece wanderson.silva@etapa.com.br, como no projeto original. Para alterá-lo, edite DESTINATARIO no Google_Email.gs e publique uma nova versão da implantação.

O Google limita o número de destinatários por dia. Se a cota acabar, o site informa o erro. Uma confirmação significa que o Google aceitou o envio, não que o destinatário leu ou recebeu na caixa principal. O saldo continua dependendo da aprovação do administrador.

Se a conta escolar não permitir Apps Script, autorização de e-mail ou acesso para Qualquer pessoa, o administrador da escola precisa liberar ou outra conta Google autorizada precisa hospedar o script. Essa restrição não pode ser corrigida apenas mudando o Python.

Em caso de timeout, confira as Execuções do Apps Script e a caixa do professor antes de repetir o pedido: o e-mail pode ter sido enviado apesar da falta de resposta. Não há repetição automática de envios.

Referências oficiais:
- https://developers.google.com/apps-script/guides/web
- https://developers.google.com/apps-script/reference/mail/mail-app
