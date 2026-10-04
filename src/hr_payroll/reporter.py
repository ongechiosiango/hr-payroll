"""Rich reporters for single payslip and batch register."""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from .calculator import PayrollResult
from .money import format_money
from .register import EmployeeRow

console = Console()


def print_payslip(result: PayrollResult, currency: str = "USD", name: str = "Employee") -> None:
    """Print a single-employee payslip."""
    console.print()
    console.rule("[bold cyan]Payslip[/bold cyan]")
    console.print(f"[bold]Employee:[/bold] {name}")
    console.print(f"[bold]Gross:[/bold] {format_money(result.gross, currency)}\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Deduction", style="cyan")
    table.add_column("Amount", style="red", justify="right")

    for d in result.deductions:
        if d.amount == 0:
            continue
        table.add_row(d.label, format_money(d.amount, currency))

    table.add_row(
        "[bold]Total Deductions[/bold]",
        f"[bold]{format_money(result.total_deductions, currency)}[/bold]",
    )
    console.print(table)

    console.print(
        f"\n[bold green]Net Pay:[/bold green] "
        f"[bold green]{format_money(result.net, currency)}[/bold green]"
    )


def print_register(rows, currency: str = "USD") -> None:
    """Print a payroll register for many employees."""
    console.print()
    console.rule("[bold cyan]Payroll Register[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Employee", style="cyan", no_wrap=True)
    table.add_column("Gross", style="white", justify="right")
    table.add_column("Deductions", style="red", justify="right")
    table.add_column("Net", style="green", justify="right")

    total_gross = total_deductions = total_net = 0

    for row in rows:
        table.add_row(
            row.name,
            format_money(row.result.gross, currency),
            format_money(row.result.total_deductions, currency),
            format_money(row.result.net, currency),
        )

    console.print(table)


def to_json(result: PayrollResult, currency: str = "USD", name: str = "Employee") -> str:
    """Serialize a single PayrollResult to JSON."""
    payload = {
        "employee": name,
        "currency": currency,
        "gross": str(result.gross),
        "deductions": [
            {"label": d.label, "amount": str(d.amount)} for d in result.deductions
        ],
        "total_deductions": str(result.total_deductions),
        "net": str(result.net),
    }
    return json.dumps(payload, indent=2)


def register_to_json(rows, currency: str = "USD") -> str:
    """Serialize a batch register to JSON."""
    payload = {
        "currency": currency,
        "employees": [
            {
                "name": row.name,
                "gross": str(row.result.gross),
                "deductions": [
                    {"label": d.label, "amount": str(d.amount)}
                    for d in row.result.deductions
                ],
                "total_deductions": str(row.result.total_deductions),
                "net": str(row.result.net),
            }
            for row in rows
        ],
    }
    return json.dumps(payload, indent=2)
