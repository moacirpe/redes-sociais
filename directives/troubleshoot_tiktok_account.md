# Directive: Resolver Problemas de Conta TikTok

## Problema
Erro "conta não existe" ao tentar fazer login no TikTok Developer Portal

## Diagnóstico Rápido

### Verificar Elegibilidade da Conta
```bash
# Verificar se a conta existe e está ativa
curl -s "https://www.tiktok.com/@{username}" | grep -o "user-id"
```

### Possíveis Causas

#### 1. Conta Business Não Configurada
- Conta pessoal não pode acessar Developer Portal
- Precisa converter para conta Business

#### 2. Conta Não Verificada
- TikTok requer verificação por email/telefone
- Conta deve ter pelo menos 30 dias

#### 3. Restrições de País/Região
- Alguns países têm restrições para Developer API
- Verificar lista de países suportados

#### 4. Conta Suspensa/Banida
- Conta violou termos de serviço
- Precisa de conta alternativa

#### 5. Conta Criada Recentemente
- TikTok requer conta com pelo menos 30 dias
- Conta deve ter atividade regular

## Soluções por Prioridade

### SOLUÇÃO 1: Verificar/Converter para Conta Business
```
No app TikTok:
1. Perfil → Configurações → Conta
2. "Alternar para conta Business"
3. Preencher informações da empresa
4. Aguardar aprovação (pode levar dias)
```

### SOLUÇÃO 2: Verificar Status da Conta
```
Checklist:
□ Email verificado
□ Telefone verificado
□ Conta tem 30+ dias
□ Conta Business ativa
□ País/região suportada
□ Sem violações de termos
```

### SOLUÇÃO 3: Conta Alternativa (se necessário)
```
Se a conta principal não funcionar:
1. Criar nova conta Business
2. Aguardar 30 dias
3. Verificar completamente
4. Tentar novamente
```

### SOLUÇÃO 4: Suporte TikTok
```
Se nada funcionar:
1. Acessar help.tiktok.com
2. Categoria: Developer/API
3. Explicar o problema
4. Aguardar resposta (dias)
```

## Verificação de País Suportado

### Países Totalmente Suportados:
- Estados Unidos
- Reino Unido
- Canadá
- Austrália
- Nova Zelândia
- Cingapura
- Japão
- Coreia do Sul

### Países com Restrições:
- Brasil (requer conta Business verificada)
- México
- Argentina
- Outros países da América Latina

### Países Não Suportados:
- Cuba
- Irã
- Síria
- Coreia do Norte
- Alguns outros

## Script de Verificação

```python
# Verificar se conta é elegível
def checkTikTokEligibility(username):
    # Verificar se conta existe
    # Verificar se é Business
    # Verificar país/região
    # Retornar status
    pass
```

## Plano B: API Alternativa

Se TikTok Developer não funcionar:

### Opção 1: TikTok Business Manager
```
- Acessar business.tiktok.com
- Criar conta Business
- Usar API através do Business Manager
- Mais limitado, mas mais fácil
```

### Opção 2: Web Scraping (último recurso)
```
- Coletar dados públicos via scraping
- Menos confiável
- Pode violar termos
- Usar apenas se API não funcionar
```

## Checklist de Troubleshooting

- [ ] Conta existe no TikTok?
- [ ] Conta é Business?
- [ ] Email/telefone verificados?
- [ ] Conta tem 30+ dias?
- [ ] País suportado?
- [ ] Sem restrições na conta?
- [ ] Testou com conta diferente?

## Contato para Suporte

### TikTok Business Support
- Email: business@tiktok.com
- Help Center: help.tiktok.com

### Developer Support
- Portal: developers.tiktok.com/support
- Documentação: developers.tiktok.com/docs

## Próximos Passos

1. Verificar status da conta atual
2. Converter para Business se necessário
3. Testar novamente
4. Usar conta alternativa se falhar
5. Contatar suporte se persistir</content>
<parameter name="filePath">/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS-/directives/troubleshoot_tiktok_account.md