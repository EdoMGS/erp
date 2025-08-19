from ljudski_resursi.models import Department, Employee, ExpertiseLevel, HierarchicalLevel, Position


def create_minimal_employee(user):
    hlevel = HierarchicalLevel.objects.create(name="H1", level=1)
    dept = Department.objects.create(name="Dept1")
    expertise = ExpertiseLevel.objects.create(name="Junior")
    position = Position.objects.create(
        title="Worker",
        department=dept,
        hierarchical_level=hlevel,
        expertise_level=expertise,
    )
    return Employee.objects.create(user=user, position=position, expertise_level=expertise, department=dept)
