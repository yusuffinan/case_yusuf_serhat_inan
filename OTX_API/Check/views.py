from django.shortcuts import render
import requests
import dns.resolver
from .models import ResultModel

def save_results(target, result_type, result_data):
    ResultModel.objects.create(target=target, result_type=result_type, result_data=result_data)

def otx_api(target):
    api_key = "a3756e3643d66bcd824681d1d260b90bd2ed00a391ddb8a0d16752ce13c16186"
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{target}/"

    #api calls https://gist.github.com/chrisdoman/3cccfbf6f07cf007271bec583305eb92

    headers = {
        "api_key":api_key
    }

    response = requests.get(url, headers=headers) 

    if response.status_code == 200:
        result = response.json()   
        
        if 'pulse_info' in result and 'count' in result['pulse_info'] and result['pulse_info']['count'] == 0:
            save_results(target,"API", "zararsiz")
            return f"{target} zararsiz"
        else:
            save_results(target, "API", "tehdit unsuru mevcut")
            return f"{target} tehdit unsuru mevcut"
    else:
        return "böyle bir veri yok."
    

def dns_query(target):
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"] #IPv4 IPv6 gibi dns kayıtları listesi.
    resolver = dns.resolver.Resolver() #Dns çözümleyici 
    results = []

    for record_type in record_types:
        try:
            answers = resolver.resolve(target, record_type) #çözümlenmek istenen dns kayıt türü.
        except dns.resolver.NoAnswer: # bu kayıttan yanıt alınmazsa continue aktarılır.
            continue
        str_result = f" {record_type} - " #her seferinde target bilgisi yer kaplıyordu onu eklemedim.
        for rdata in answers:
            str_result += f" {rdata} " #answer'in içindeki bilgileri str olarak ekler.
        results.append((str_result))

    save_results(target, "DNS", str(results)) 
    return results

def index(request):
    results = []

    if request.method == "POST":
        target = request.POST.get("target", "") #target required olsa da güvenlik ve garanticilik için böyle yaptım.
        check_api = otx_api(target)
        results.append(("API", check_api)) 

        dns = dns_query(target)
        results.append(("DNS", dns))
    

    return render(request, "index.html", {
        "results": results,
        })

def show_history(request):
    history = ResultModel.objects.all()[::-1]

    return render(request, "history.html", {
        "history": history,
        })


def past_fifty(request):
    history = ResultModel.objects.all()[::-1][:102] #burada 102 yazdım çünkü verilerin biri api diğeri dns bilgileri.
    zararli_count = sum(1 for item in history if item.result_data == "tehdit unsuru mevcut")
    zararli_degil_count = sum(1 for item in history if item.result_data == "zararsiz") #Queryset olduğu için history.filter kullanılmıyor.
    
    total_count = zararli_count + zararli_degil_count
    zararli_percentage = (zararli_count / total_count) * 100
    zararli_degil_percentage = (zararli_degil_count / total_count) * 100

    return render(request, "graphic.html", {
        "history": history,
        "zararli_percentage": zararli_percentage,
        "zararli_degil_percentage": zararli_degil_percentage
    })

def result_graphic(request):
    results = ResultModel.objects.all()
    zararli = results.filter(result_data="tehdit unsuru mevcut").count()
    zararsiz = results.filter(result_data="zararsiz").count()
    
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"]
    #contains kullanarak result_type'ı DNS olanların result_data içinde record geçenleri topladım.
    record_counts = [results.filter(result_type="DNS", result_data__contains=record).count() for record in record_types]

    dns = results.filter(result_type="DNS").count()
    dns_list = dict(zip(record_types,record_counts)) # iki listeyi zip ile eşleştirdim.

    return render(request, "result_graphic_all.html", {
        "zararli":zararli,
        "zararsiz":zararsiz,
        "record_types":record_types,
        "record_counts":record_counts,
        "dns":dns,
        "dns_list":dns_list
    })