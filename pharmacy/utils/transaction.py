from pharmacy.models import TransactionMainsTemps

    

def generate_tran_id(prefix="TRA"):
   

    # Find the last TRAXXXXX row
    last_tran = TransactionMainsTemps.objects.filter(
        tran_id__startswith=prefix
    ).order_by('-tran_id').first()

    if last_tran:
        last_num_str = last_tran.tran_id.replace(prefix, "")
        try:
            last_num = int(last_num_str)
        except ValueError:
            last_num = 0
    else:
        last_num = 0

    new_num = last_num + 1
    return f"{prefix}{str(new_num).zfill(9)}"
