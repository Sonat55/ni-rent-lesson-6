import argparse
import sys

from src.manager import Manager
from src.models import Parameters


def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_subsection_header(title: str):
    """Print a formatted subsection header"""
    print(f"\n  {title}")
    print(f"  {'-' * 40}")


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{amount:,.2f} PLN"


def display_apartments(manager):
    """Display all apartments with their rooms and bills"""
    print_section_header("APARTMENTS")
    
    for apartment in manager.apartments.values():
        print(f"\n📍 {apartment.name} ({apartment.key})")
        print(f"   Location: {apartment.location}")
        print(f"   Total Area: {apartment.area_m2} m²")
        
        print_subsection_header("Rooms")
        for room in apartment.rooms.values():
            print(f"      • {room.name:<25} {room.area_m2:>6} m²")
        
        # Find bills for this apartment
        apartment_bills = [bill for bill in manager.bills if bill.apartment == apartment.key]
        if apartment_bills:
            print_subsection_header("Bills")
            for bill in apartment_bills:
                month_year = f"{bill.settlement_month}/{bill.settlement_year}" if bill.settlement_month and bill.settlement_year else "N/A"
                print(f"      • {bill.type:<15} {format_currency(bill.amount_pln):>15}  Due: {bill.date_due}  Period: {month_year}")


def display_tenants(manager):
    """Display all tenants with their details and transfers"""
    print_section_header("TENANTS")
    
    for tenant in manager.tenants.values():
        print(f"\n👤 {tenant.name}")
        print(f"   Apartment: {tenant.apartment}")
        print(f"   Room: {tenant.room}")
        print(f"   Rent: {format_currency(tenant.rent_pln)}/month")
        print(f"   Deposit: {format_currency(tenant.deposit_pln)}")
        print(f"   Agreement: {tenant.date_agreement_from} to {tenant.date_agreement_to}")
        
        # Find transfers for this tenant
        tenant_transfers = [transfer for transfer in manager.transfers if transfer.tenant == tenant.name]
        if tenant_transfers:
            print_subsection_header("Transfers")
            for transfer in tenant_transfers:
                month_year = f"{transfer.settlement_month}/{transfer.settlement_year}" if transfer.settlement_month and transfer.settlement_year else "N/A"
                print(f"      • {format_currency(transfer.amount_pln):>15}  Date: {transfer.date}  Period: {month_year}")


def display_settlement(manager, apartment_key: str, year: int, month: int) -> bool:
    """Display the settlement of one apartment for one month. Returns False on error."""
    try:
        settlement = manager.get_settlement(apartment_key, year, month)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return False
    if settlement is None:
        print(f"Error: unknown apartment '{apartment_key}'. "
              f"Available: {', '.join(manager.apartments)}", file=sys.stderr)
        return False

    print_section_header(f"SETTLEMENT {apartment_key} {month:02d}/{year}")
    print(f"\n  Total due: {format_currency(settlement.total_due_pln)}")

    tenant_settlements = manager.create_tenants_settlements(settlement) or []
    print_subsection_header("Per tenant")
    if not tenant_settlements:
        print("      (no tenants in this apartment)")
    for tenant_settlement in tenant_settlements:
        print(f"      • {tenant_settlement.tenant:<25} {format_currency(tenant_settlement.total_due_pln):>15}")

    debtors = manager.get_debtors(apartment_key, month, year) or []
    print_subsection_header("Debtors")
    if debtors:
        for name in debtors:
            print(f"      • {name}")
    else:
        print("      (none)")
    return True


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Show the rent settlement for an apartment and month.")
    parser.add_argument("apartment", help="apartment key, e.g. apartment-1")
    parser.add_argument("year", type=int, help="settlement year, e.g. 2024")
    parser.add_argument("month", type=int, help="settlement month (1-12)")
    return parser.parse_args(argv)


if __name__ == '__main__':
    args = parse_args()
    manager = Manager(Parameters())
    ok = display_settlement(manager, args.apartment, args.year, args.month)
    print(f"\n{'=' * 70}\n")
    sys.exit(0 if ok else 1)