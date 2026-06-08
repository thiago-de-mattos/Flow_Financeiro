from django.shortcuts import render

def inicio(request):

    context = { 'nome_usuario': 'Júnior', 'tecnologias': ['Python', 'Django', 'HTML', 'CSS'] } 

    return render(request, 'inicio.html',context) 