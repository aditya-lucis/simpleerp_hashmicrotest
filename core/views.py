from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounting.models import Account, JournalDetail

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            
            messages.error(request, 'Username atau password salah!')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'index.html')

@login_required(login_url='login')
def dashboard(request):
    journal_details = JournalDetail.objects.select_related('account').all()
    accounts = Account.objects.all().order_by('code')
    
    total_asset = 0.0
    total_liability = 0.0
    total_equity = 0.0
    total_revenue = 0.0
    total_expense = 0.0
    
    # Kalkulasi 5 Pilar Utama
    for detail in journal_details:
        val_debit = float(detail.debit)
        val_credit = float(detail.credit)
        acc_type = detail.account.account_type
        
        if acc_type == 'Asset': total_asset += (val_debit - val_credit)
        elif acc_type == 'Liability': total_liability += (val_credit - val_debit)
        elif acc_type == 'Equity': total_equity += (val_credit - val_debit)
        elif acc_type == 'Revenue': total_revenue += (val_credit - val_debit)
        elif acc_type == 'Expense': total_expense += (val_debit - val_credit)

    net_profit = total_revenue - total_expense

    # --- Rekap Saldo per COA (Trial Balance) ---
    account_balances = []
    for acc in accounts:
        details = journal_details.filter(account=acc)
        tot_deb = sum(float(d.debit) for d in details)
        tot_cred = sum(float(d.credit) for d in details)
        
        balance = 0.0
        
        if acc.account_type in ['Asset', 'Expense']:
            balance = tot_deb - tot_cred
        else:
            balance = tot_cred - tot_deb
            
        if tot_deb > 0 or tot_cred > 0:
            account_balances.append({
                'code': acc.code,
                'name': acc.name,
                'type': acc.account_type,
                'debit': tot_deb,
                'credit': tot_cred,
                'balance': balance
            })

    context = {
        'total_asset': total_asset,
        'total_liability': total_liability,
        'total_equity': total_equity,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'account_balances': account_balances,
    }
    
    return render(request, 'index.html', context)