"""
Opportunity Cost Calculator — projects the compounded future value of an amount
if invested instead of spent, using a fixed annual rate of return.
"""

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from JWT_Authentication.auth import get_current_user

router_opportunity_cost = APIRouter()

# Fixed assumption, per proposal's explicit limitation (no market variability).
DEFAULT_ANNUAL_RATE = 0.08  # 8% — a commonly cited long-term average return


class OpportunityCostInput(BaseModel):
    amount: float = Field(
        ..., gt=0, description="The amount that would otherwise be spent."
    )
    years: float = Field(
        ..., gt=0, description="Number of years to project growth over."
    )
    annual_rate: float | None = Field(
        None,
        description="Optional custom annual rate of return as a decimal (e.g. 0.08 for 8%). Defaults to 8% if omitted.",
    )
    contribution_frequency: int = Field(
        12,
        description="Compounding periods per year. Defaults to 12 (monthly compounding).",
    )


@router_opportunity_cost.post(
    "/calculate",
    summary="Calculate the opportunity cost of a one-time expense",
    description="Projects the compounded future value of an amount if invested instead of spent, using a fixed annual rate of return.",
)
def calculate_opportunity_cost(
    payload: OpportunityCostInput,
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate compounded future value of a lump sum under a fixed rate of return.

    Args:
        payload (OpportunityCostInput): amount, years, optional annual_rate, and compounding frequency.
        current_user (dict): The current authenticated user (calculator is stateless, not persisted).

    Returns:
        dict: original amount, assumed rate, years, projected future value, and total growth.
    """
    rate = (
        payload.annual_rate if payload.annual_rate is not None else DEFAULT_ANNUAL_RATE
    )
    n = payload.contribution_frequency

    # Standard compound interest formula: FV = P * (1 + r/n)^(n*t)
    future_value = payload.amount * ((1 + rate / n) ** (n * payload.years))

    return {
        "original_amount": round(payload.amount, 2),
        "annual_rate_used": rate,
        "years": payload.years,
        "compounding_periods_per_year": n,
        "projected_future_value": round(future_value, 2),
        "total_growth": round(future_value - payload.amount, 2),
    }


@router_opportunity_cost.post(
    "/recurring-calculate",
    summary="Calculate the opportunity cost of a recurring expense",
    description="Projects the compounded future value of a fixed amount contributed periodically, if invested instead of spent.",
)
def calculate_recurring_opportunity_cost(
    payload: OpportunityCostInput,
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate compounded future value of periodic contributions under a fixed rate of return.

    Args:
        payload (OpportunityCostInput): per-period amount, years, optional annual_rate, and compounding frequency.
        current_user (dict): The current authenticated user (calculator is stateless, not persisted).

    Returns:
        dict: per-period amount, assumed rate, years, total contributed, projected future value, and total growth.
    """
    rate = (
        payload.annual_rate if payload.annual_rate is not None else DEFAULT_ANNUAL_RATE
    )
    n = payload.contribution_frequency
    total_periods = n * payload.years
    period_rate = rate / n

    # Future value of a periodic contribution series (ordinary annuity):
    # FV = P * [((1 + r/n)^(n*t) - 1) / (r/n)]
    if period_rate > 0:
        future_value = payload.amount * (
            ((1 + period_rate) ** total_periods - 1) / period_rate
        )
    else:
        future_value = payload.amount * total_periods

    total_contributed = payload.amount * total_periods

    return {
        "amount_per_period": round(payload.amount, 2),
        "annual_rate_used": rate,
        "years": payload.years,
        "compounding_periods_per_year": n,
        "total_contributed": round(total_contributed, 2),
        "projected_future_value": round(future_value, 2),
        "total_growth": round(future_value - total_contributed, 2),
    }
