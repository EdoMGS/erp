from nalozi.models import RadniNalog, Materijal

def check_resources(task_id):
    task = RadniNalog.objects.get(pk=task_id)
    materials_needed = task.materijali.all()
    for material in materials_needed:
        if not material.na_stanju:
            task.razlog_kasnjenja = "Nedostatak materijala: " + material.naziv_materijala
            task.save()
            return False
    return True
