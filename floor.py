"""
Gets the floor price for #LoadedLions as well as a configurable amount of the cheapest lions marked as 'Buy now'
"""
from decimal import Decimal
from time import sleep

import requests

URL = "https://crypto.com/nft-api/graphql"

lion_count = 0
LIONS_TO_FETCH = 20


def get_floor_price() -> Decimal:
    r = requests.post(
        URL,
        json={
            "operationName": "GetCollection",
            "variables": {"collectionId": "82421cf8e15df0edcaa200af752a344f"},
            "query": "query GetCollection($collectionId: ID!) {\n  public {\n    collection(id: $collectionId) {\n      id\n      name\n      description\n      categories\n      banner {\n        url\n        __typename\n      }\n      logo {\n        url\n        __typename\n      }\n      creator {\n        displayName\n        __typename\n      }\n      aggregatedAttributes {\n        label: traitType\n        options: attributes {\n          value: id\n          label: value\n          total\n          __typename\n        }\n        __typename\n      }\n      metrics {\n        items\n        minAuctionListingPriceDecimal\n        minSaleListingPriceDecimal\n        owners\n        totalSalesDecimal\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        },
    )

    return Decimal(
        r.json()["data"]["public"]["collection"]["metrics"][
            "minSaleListingPriceDecimal"
        ]
    )


def get_assets(min_price: int, skip=0):
    """
    Returns 10 items by ASC price; to grab more than 10, increment the skip parameter
    """
    r = requests.post(
        URL,
        json={
            "operationName": "GetAssets",
            "variables": {
                "collectionId": "82421cf8e15df0edcaa200af752a344f",
                "first": 10,
                "skip": skip,
                "cacheId": "getAssetsQuery-b1223f55c176ddc4d379fc964eca83a9252268f8",
                "hasSecondaryListing": True,
                "where": {
                    "assetName": None,
                    "description": None,
                    "minPrice": f"{min_price}",
                    "maxPrice": None,
                    "attributes": [],
                },
                "sort": [{"order": "ASC", "field": "price"}],
            },
            "query": "fragment UserData on User {\n  uuid\n  id\n  username\n  displayName\n  isCreator\n  avatar {\n    url\n    __typename\n  }\n  __typename\n}\n\nquery GetAssets($audience: Audience, $brandId: ID, $categories: [ID!], $collectionId: ID, $creatorId: ID, $ownerId: ID, $first: Int!, $skip: Int!, $cacheId: ID, $hasSecondaryListing: Boolean, $where: AssetsSearch, $sort: [SingleFieldSort!], $isCurated: Boolean, $createdPublicView: Boolean) {\n  public(cacheId: $cacheId) {\n    assets(\n      audience: $audience\n      brandId: $brandId\n      categories: $categories\n      collectionId: $collectionId\n      creatorId: $creatorId\n      ownerId: $ownerId\n      first: $first\n      skip: $skip\n      hasSecondaryListing: $hasSecondaryListing\n      where: $where\n      sort: $sort\n      isCurated: $isCurated\n      createdPublicView: $createdPublicView\n    ) {\n      id\n      name\n      copies\n      copiesInCirculation\n      creator {\n        ...UserData\n        __typename\n      }\n      main {\n        url\n        __typename\n      }\n      cover {\n        url\n        __typename\n      }\n      royaltiesRateDecimal\n      primaryListingsCount\n      secondaryListingsCount\n      primarySalesCount\n      secondarySalesCount\n      primaryAuctionsCount\n      secondaryAuctionsCount\n      totalSalesDecimal\n      defaultListing {\n        editionId\n        priceDecimal\n        mode\n        auctionHasBids\n        __typename\n      }\n      defaultAuctionListing {\n        editionId\n        priceDecimal\n        mode\n        auctionHasBids\n        __typename\n      }\n      defaultSaleListing {\n        editionId\n        priceDecimal\n        mode\n        __typename\n      }\n      defaultPrimaryListing {\n        editionId\n        priceDecimal\n        mode\n        auctionHasBids\n        primary\n        __typename\n      }\n      defaultSecondaryListing {\n        editionId\n        priceDecimal\n        mode\n        auctionHasBids\n        __typename\n      }\n      defaultSecondaryAuctionListing {\n        editionId\n        priceDecimal\n        mode\n        auctionHasBids\n        __typename\n      }\n      defaultSecondarySaleListing {\n        editionId\n        priceDecimal\n        mode\n        __typename\n      }\n      likes\n      views\n      isCurated\n      defaultEditionId\n      __typename\n    }\n    __typename\n  }\n}\n",
        },
    )

    assets = r.json()["data"]["public"]["assets"]
    return assets


lowest_price = get_floor_price()
print(f"Floor price is currently ${lowest_price}\n")
print(f"Getting the cheapest {LIONS_TO_FETCH} lions:")

skip_multi = 0

while True:
    for asset in get_assets(lowest_price - 1, skip_multi * 10):
        lion_name = asset["name"]
        asset_id = asset["id"]

        default_listing = asset["defaultListing"]
        edition_id = default_listing["editionId"]
        mode_sale = (default_listing["mode"] == "sale")
        price = default_listing["priceDecimal"]
        
        # check if it is buy it now
        if not mode_sale:
            continue
            
        print(f"{lion_count + 1} - {lion_name.ljust(18, ' ')} Price: ${price}")
        lion_count += 1
        if lion_count == LIONS_TO_FETCH:
          exit()
    sleep(0.1)
    skip_multi += 1