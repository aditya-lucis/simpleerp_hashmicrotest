from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Account, JournalHeader, JournalDetail
from datetime import date, datetime

# 1. CoA Module

# 1.1 CoA Page
@login_required(login_url='login')
def coa_page(request):
    return render(request, 'accounting/coa_list.html')

# 1.2 List of CoA
@login_required(login_url='login')
def coa_json(request):
    accounts = Account.objects.all().order_by('code')
    data = []
    for acc in accounts:
        data.append({
            'id': acc.id,
            'code': acc.code,
            'name': acc.name,
            'account_type': acc.account_type,
        })
    return JsonResponse({'data': data})

# 1.3 CoA Form (Create/Update)
@login_required(login_url='login')
def coa_save_ajax(request):
    if request.method == 'POST':
        acc_id = request.POST.get('id')
        name = request.POST.get('name')
        account_type = request.POST.get('account_type')

        try:
            if acc_id:  # Mode Edit
                acc = Account.objects.get(pk=acc_id)
                acc.name = name
                acc.account_type = account_type
                acc.save()
                return JsonResponse({'status': 'success', 'message': 'Data CoA berhasil diupdate!'})
            else:  # Mode Create
                last_coa = Account.objects.filter( code__startswith='17.02.02.' ).order_by('id').last()
                if last_coa:
                    try:
                        last_part = last_coa.code.split('.')[-1]
                        last_number = int(last_part)
                        new_number = last_number + 1
                    except (IndexError, ValueError):
                        new_number = 1

                    new_code = f"17.02.02.{new_number:02d}"
                else:
                    new_code = "17.02.02.01"

                Account.objects.create(code=new_code, name=name, account_type=account_type)
                return JsonResponse({'status': 'success', 'message': 'Akun baru berhasil ditambahkan!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
# 1.4 CoA Delete
@login_required(login_url='login')
def coa_delete_ajax(request, pk):
    if request.method == 'POST':
        try:
            acc = Account.objects.get(pk=pk)
            acc.delete()
            return JsonResponse({'status': 'success', 'message': 'Data CoA berhasil dihapus!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

# 2. Journal Module

# 2.1 create general journal entry
@login_required(login_url='login')
def journal_create(request):

    accounts = Account.objects.all()

    today_str = date.today().strftime('%d%m%Y')
    last_journal = JournalHeader.objects.filter( reference__startswith='GEJ' ).order_by('id').last()

    if last_journal:
        last_number = int(last_journal.reference.split('-')[1])
        new_number = last_number + 1
    else:
        new_number = 1

    default_reference = f"GEJ{today_str}-{new_number:04d}"

    if request.method == 'POST':
        
        date_str = request.POST.get('date')
        description = request.POST.get('description')

        reference = default_reference

        account_ids = request.POST.getlist('account_id[]')
        debits = request.POST.getlist('debit[]')
        credits = request.POST.getlist('credit[]')

        total_debit = 0.0
        total_credit = 0.0

        batch_transactions = [{
            'lines': zip(account_ids, debits, credits)
        }]

        error_message = None

        for tx in batch_transactions:
            for acc_id, deb, cred in tx['lines']:
                val_deb = float(deb) if deb else 0.0
                val_cred = float(cred) if cred else 0.0

                if val_deb > 0 or val_cred > 0:
                    if val_deb > 0 and val_cred > 0:
                        error_message = "Error: Satu baris tidak boleh diisi Debit dan Kredit sekaligus!"
                        break

                total_debit += val_deb
                total_credit += val_cred

        if error_message:
            messages.error(request, error_message)
        elif abs(total_debit - total_credit) > 0.01:
            messages.error(request, f"Jurnal tidak balance! Total Debit: {total_debit} | Total Kredit: {total_credit}")
        elif total_debit == 0:
            messages.error(request, "Nilai jurnal tidak boleh kosong!")
        else:
            
            header = JournalHeader.objects.create(
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                reference=reference,
                description=description,
                total_amount=total_debit
            )
            
            lines_to_save = zip(account_ids, debits, credits)
            for acc_id, deb, cred in lines_to_save:
                val_deb = float(deb) if deb else 0.0
                val_cred = float(cred) if cred else 0.0
                if val_deb > 0 or val_cred > 0:
                    JournalDetail.objects.create(
                        header=header,
                        account_id=int(acc_id),
                        debit=val_deb,
                        credit=val_cred
                    )
            messages.success(request, "General Journal berhasil disimpan!")
            return redirect('journal_list')
        
    return render(request, 'accounting/journal_form.html', {'accounts': accounts, 'default_reference': default_reference, 'today_str': date.today().isoformat()})

# 2.2 page of list of general journal entries
@login_required(login_url='login')
def journal_list(request):
    today = datetime.today()
    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
        (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember')
    ]
    years = range(today.year - 2, today.year + 2)

    context = {
        'selected_month': today.month,
        'selected_year': today.year,
        'months': months,
        'years': years,
    }
    return render(request, 'accounting/journal_list.html', context)

# 2.3 Ajax datatable list of general journal
@login_required(login_url='login')
def journal_json(request):
    today = datetime.today()

    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    journals = JournalHeader.objects.filter( date__month=selected_month, date__year=selected_year ).order_by('-date', '-created_at')

    data = []
    for j in journals:
        data.append({
            'date': j.date.strftime('%d-%m-%Y'), # Format tanggal
            'reference': j.reference,
            'description': j.description if j.description else "-",
            'total_amount': f"{j.total_amount:,.2f}" # Format angka ribuan
        })
    return JsonResponse({'data': data})

# 3. String Analyzer

# 3.1 String Analyzer Page
@login_required(login_url='login')
def string_analyzer(request):
    return render(request, 'accounting/string_analyzer.html')

# 3.2 String Analyzer Ajax
@login_required(login_url='login')
def string_analyzer_ajax(request):
    if request.method == 'POST':
        input1 = request.POST.get('input1', '')
        input2 = request.POST.get('input2', '')
        case_type = request.POST.get('case_type', 'sensitive')

        if not input1:
            return JsonResponse({'status': 'error', 'message': 'Input 1 tidak boleh kosong'})

        match_count = 0
        len_input1 = len(input1)

        # Algoritma perhitungan (Nested Loop & Nested If)
        for char1 in input1:
            found_in_loop = False
            for char2 in input2:
                if case_type == 'sensitive':
                    if char1 == char2:
                        found_in_loop = True
                        break
                else:
                    if char1.lower() == char2.lower():
                        found_in_loop = True
                        break
            if found_in_loop:
                match_count += 1

        percentage = (match_count / len_input1) * 100

        return JsonResponse({
            'status': 'success',
            'input1': input1,
            'input2': input2,
            'case_type': case_type,
            'percentage': f"{percentage:.0f}%"
        })