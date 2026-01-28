from django import forms
from django.contrib.auth.models import User
from .models import Perfil, Associado, TimelinePost


#=====================================================
# CLASSE FORM - PERFIL
#====================================================

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'perfil_razaosocial',
            'perfil_nomefantasia',
            'perfil_cnpj',
            'perfil_email',
            'perfil_endereco',
            'perfil_numero',
            'perfil_complemento',
            'perfil_bairro',
            'perfil_cidade',
            'perfil_cep',
            'perfil_uf',
            'perfil_telefone1',
            'perfil_telefone2',
            'perfil_datafundacao',            

        ]
        labels = {
            'perfil_razaosocial': 'Razão Social',
            'perfil_nomefantasia': 'Nome Fantasia',
            'perfil_cnpj': 'CNPJ',
            'perfil_email': 'E-mail',
            'perfil_endereco': 'Endereço',
            'perfil_numero': 'Número',
            'perfil_complemento': 'Complemento',
            'perfil_bairro': 'Bairro',
            'perfil_cidade': 'Cidade',
            'perfil_cep': 'CEP',
            'perfil_uf': 'UF',
            'perfil_telefone1': 'Telefone 1',
            'perfil_telefone2': 'Telefone 2',
            'perfil_datafundacao': 'Data de Fundação',
            
        }

        widgets = {
             'perfil_datafundacao': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'perfil_datacadastro': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),

            'perfil_razaosocial': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 3px; font-size: 14px;',
            }),

            'perfil_endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 3px; font-size: 14px;',
            }),
            
            'perfil_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 3px; font-size: 14px;',
            }),
            
            'perfil_complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 3px; font-size: 14px;',
            }),

            'perfil_cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_perfil_cnpj',
                'placeholder': '00.000.000/0000-00',
                'style': 'width: 100%; padding: 3px; font-size: 14px;',
            }),

            'perfil_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_perfil_cep',
                'placeholder': '00000-000',
                'style': 'width: 100%; padding: 3px; font-size: 12px;',
            }),

            'perfil_telefone1': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_perfil_telefone',
                'placeholder': '(00) 00000-0000',
                'style': 'width: 100%; padding: 3px; font-size: 12px;',
            }),
            
            'perfil_telefone2': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_perfil_telefone',
                'placeholder': '(00) 00000-0000',
                'style': 'width: 100%; padding: 3px; font-size: 12px;',
            }),
            
        }
#======================================================================================================================

#=====================================================================================================================
# CLASS FORM - REGISTER - ASSOCIADO
#=====================================================================================================================

class AssociadoForm(forms.ModelForm):

    class Meta:
        model = Associado
        fields = [
            'associado_nome',
            'associado_email',
            'associado_telefone',
            'tipoassociado',           
            'associado_observacoes',           
        ]

        labels = {
            'associado_nome': 'Nome',
            'associado_email': 'E-mail',
            'associado_telefone': 'Telefone',
            'tipoassociado': 'Tipo de Associado',            
            'associado_observacoes': 'Observações',                    
        }

        widgets = {
            'associado_nome': forms.TextInput(attrs={
                'placeholder': 'Nome fantasia',
                'class': 'form-control'
            }),
            'associado_email': forms.EmailInput(attrs={
                'placeholder': 'E-mail',
                'class': 'form-control'
            }),
            'associado_telefone': forms.TextInput(attrs={
                'placeholder': 'Telefone / WhatsApp',
                'class': 'form-control'
            }),
            'tipoassociado': forms.Select(attrs={
                'class': 'form-control'
            }),
            
            'associado_observacoes': forms.Textarea(attrs={
                'placeholder': 'Observações (opcional)',
                'rows': 4,
                'class': 'form-control'
            
            }),
        }

        

#=====================================================================================================================

#=====================================================
# CLASSE FORM - ADM INPRIVY - ASSOCIADO
#=====================================================
class AssociadoAdminForm(forms.ModelForm):
    class Meta:
        model = Associado
        fields = [
            'associado_nome',
            'tipoassociado',            
            'associado_email',            
            'associado_telefone',
            'tipoplano',            
            'associado_observacoes',
            'associado_codigo', 
            'status',          
            
        ]

        labels = {
            'associado_nome': 'Nome Fantasia',
            'tipoassociado': 'Tipo de Associado',            
            'associado_email': 'E-mail',            
            'associado_telefone': 'Telefone',
            'tipoplano': 'Tipo de Plano',
            'associado_observacoes': 'Observações',
            'status': 'Status Associação',
            
        }

        widgets = {
             
            'associado_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 3px; font-size: 13px;',
            }),

            'tipoassociado': forms.Select(attrs={
                'class': 'form-select',
                'style': 'width: 100%; padding: 3px; font-size: 14px;',
            }),

            'associado_email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'style': 'width: 100%; padding: 3px; font-size: 13px;',
                }
            ),           
                       
            'associado_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_pessoa_telefone',
                'placeholder': '(00) 00000-0000',
                'style': 'width: 100%; padding: 3px; font-size: 13px;',
            }),
                        
            'tipoplano': forms.Select(attrs={
                'class': 'form-select',
                'style': 'width: 100%; padding: 3px; font-size: 14px;',
            }),
            
            'associado_observacoes': forms.Textarea(attrs={
                'rows': 4,
                'style': 'width: 100%;',
                'placeholder': 'Descreva Sobre a Pessoa com Detalhes...',
                'class': 'form-control',
                'style': 'width: 100%; padding: 10px; font-size: 13px;',
            }),            
            
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),                                   
        }
#======================================================================================================================

#=====================================================
# CLASSE FORM - TIMELINE POSTAGEM
#====================================================
class TimelinePostForm(forms.ModelForm):
    class Meta:
        model = TimelinePost
        fields = ['texto', 'imagem', 'video']

    texto = forms.CharField(
        required=False,  # agora texto não é obrigatório
        widget=forms.Textarea(attrs={'placeholder': 'No que você está pensando?'}),
    )
#======================================================================================================================

#=====================================================
# CLASSE FORM - MEU PERFIL(ASSOCIADO)
#=====================================================
class MeuPerfilForm(forms.ModelForm):
    class Meta:
        model = Associado
        fields = [
            'associado_nome',
            'associado_email',       # email editável
            'tipoassociado',
            'associado_telefone',
            'associado_uf',           
            'associado_observacoes',
            'associado_avatar',
        ]
        widgets = {
            'associado_nome': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'associado_email': forms.EmailInput(attrs={'placeholder': 'E-mail'}),
            'associado_telefone': forms.TextInput(attrs={'placeholder': 'Telefone'}),
            'associado_uf': forms.TextInput(attrs={'placeholder': 'UF'}),
            'associado_observacoes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observações'}),
        }

#======================================================================================================================

