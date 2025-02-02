from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from src.component.local import get_all_local_cards, view_a_report_on_local
from src.component.remote import get_all_s3_cards, download_s3_folder

router = APIRouter()


@router.get("/cards/", response_class=JSONResponse, status_code=200)
async def get_all_cards(
  source: str = Query(
    ...,
    title="Source",
    description="Retrieve all the HTML & JSON reports from the source",
    example="local/remote",
  ),
  filter: int = Query(
    ...,
    title="Filter",
    description="Filter the reports age based on the given string",
    example=7,
  ),
):
  """Get available report cards based on the source requested"""
  print(f"Report Source: {source}")
  if source == "remote":
    s3_cards = get_all_s3_cards(filter)
    return s3_cards
  else:
    return get_all_local_cards(filter)


@router.get("/card/", response_class=PlainTextResponse, status_code=200)
async def get_a_card(
  source: str = Query(
    ...,
    title="Source",
    description="Source of the html report file to be retrieved",
    example="local/remote",
  ),
  root_dir: str = Query(
    None,
    title="Root Directory",
    description="Root directory of the report to be retrieved",
    example="2021-09-01T14:00:00",
  ),
):
  """Start the playwright report view server to see the report content when 'View Report' button is clicked"""
  if source == "remote":
    test_report_dir = download_s3_folder(root_dir)
  else:
    test_report_dir = root_dir

  output = await view_a_report_on_local(test_report_dir)
  return output
