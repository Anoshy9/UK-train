#!/usr/bin/env python3
"""
Script to check UK train delays using TransportAPI (Free tier: 30 requests/day)
Requires: requests, python-dotenv

API Documentation: https://developer.transportapi.com/
"""

import os
import requests
import datetime
from typing import Optional, Dict, Any, List


BASE_URL = "https://transportapi.com/v3/uk"


def get_api_credentials() -> tuple:
    """Get API credentials from environment"""
    app_id = os.getenv('TRANSPORT_API_ID')
    app_key = os.getenv('TRANSPORT_API_KEY')
    
    if not app_id or not app_key:
        raise ValueError(
            "TRANSPORT_API_ID and TRANSPORT_API_KEY must be set. "
            "Get them from https://developer.transportapi.com/"
        )
    return app_id, app_key


def get_station_code(station_name: str, app_id: str, app_key: str) -> Optional[str]:
    """
    Get station code (CRS) from station name
    
    Args:
        station_name: Name or partial name of the station
        app_id: TransportAPI app ID
        app_key: TransportAPI app key
    
    Returns:
        Station CRS code (e.g., 'VIC' for Victoria) or None
    """
    try:
        url = f"{BASE_URL}/places.json"
        params = {
            'query': station_name,
            'type': 'train_station',
            'app_id': app_id,
            'app_key': app_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'member' in data and len(data['member']) > 0:
            return data['member'][0]['station_code']
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting station code: {e}")
        return None


def get_train_departures(from_station: str, to_station: str, app_id: str, app_key: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get live departures from a station to a destination
    
    Args:
        from_station: Departure station CRS code (e.g., 'VIC')
        to_station: Destination station CRS code (e.g., 'KGX')
        app_id: TransportAPI app ID
        app_key: TransportAPI app key
    
    Returns:
        List of train services or None if error
    """
    try:
        url = f"{BASE_URL}/train/station/{from_station}/live.json"
        params = {
            'destination': to_station,
            'app_id': app_id,
            'app_key': app_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'departures' in data and 'all' in data['departures']:
            return data['departures']['all']
        
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error getting departures: {e}")
        return None


def find_next_train(departures: List[Dict[str, Any]], target_time: Optional[str] = None, operator_filter: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Find the next departing train, optionally filtered by operator
    
    Args:
        departures: List of departure data
        target_time: Optional target departure time (HH:MM format)
        operator_filter: Optional operator name to filter by (e.g., "London Northwest Railway")
    
    Returns:
        Next train info or None
    """
    if not departures:
        return None
    
    now = datetime.datetime.now()
    target_dt = None
    
    if target_time:
        try:
            hour, minute = map(int, target_time.split(':'))
            target_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target_dt < now:
                target_dt = target_dt + datetime.timedelta(days=1)
        except (ValueError, AttributeError):
            target_dt = None
    
    best_train = None
    best_diff = float('inf')
    
    for train in departures:
        if 'aimed_departure_time' not in train:
            continue
        
        # Filter by operator if specified
        if operator_filter:
            operator_name = train.get('operator_name', '')
            if operator_filter.lower() not in operator_name.lower():
                continue
        
        dep_time_str = train['aimed_departure_time']
        try:
            dep_time = datetime.datetime.strptime(dep_time_str, '%H:%M')
            dep_time = now.replace(hour=dep_time.hour, minute=dep_time.minute, second=0, microsecond=0)
            
            if dep_time < now:
                dep_time = dep_time + datetime.timedelta(days=1)
            
            diff = abs((dep_time - (target_dt or now)).total_seconds())
            
            if diff < best_diff:
                best_diff = diff
                best_train = train
        except (ValueError, TypeError):
            continue
    
    return best_train


def format_delay_message(train: Dict[str, Any]) -> str:
    """Format a human-readable message about train status"""
    if not train:
        return "❌ No train information found"
    
    operator = train.get('operator', 'Unknown')
    train_id = train.get('train_uid', train.get('service_id', 'Unknown'))
    aimed_dep = train.get('aimed_departure_time', 'N/A')
    expected_dep = train.get('expected_departure_time', aimed_dep)
    aimed_arr = train.get('aimed_arrival_time', 'N/A')
    expected_arr = train.get('expected_arrival_time', aimed_arr)
    origin = train.get('origin_name', 'Unknown')
    destination = train.get('destination_name', 'Unknown')
    platform = train.get('platform', 'TBA')
    
    # Check if delayed
    is_delayed = (
        expected_dep != aimed_dep or 
        expected_arr != aimed_arr or 
        train.get('is_cancelled', False)
    )
    
    # Calculate delay
    delay_minutes = 0
    if expected_dep != aimed_dep and expected_dep != 'N/A' and aimed_dep != 'N/A':
        try:
            dep_aimed = datetime.datetime.strptime(aimed_dep, '%H:%M')
            dep_expected = datetime.datetime.strptime(expected_dep, '%H:%M')
            delay_minutes = int((dep_expected - dep_aimed).total_seconds() / 60)
        except ValueError:
            pass
    
    if train.get('is_cancelled', False):
        return (f"❌ **TRAIN CANCELLED** ❌\n\n"
                f"Train {train_id} ({operator})\n"
                f"{origin} → {destination}\n"
                f"Planned: {aimed_dep} | Platform: {platform}")
    
    if is_delayed and delay_minutes > 0:
        return (f"⚠️ **TRAIN DELAYED** ⚠️\n\n"
                f"Train {train_id} ({operator})\n"
                f"{origin} → {destination}\n"
                f"Planned: {aimed_dep} | Expected: {expected_dep}\n"
                f"Platform: {platform}\n"
                f"**Delay: {delay_minutes} minutes**")
    else:
        return (f"✅ **TRAIN ON TIME** ✅\n\n"
                f"Train {train_id} ({operator})\n"
                f"{origin} → {destination}\n"
                f"Departure: {aimed_dep} | Platform: {platform}\n"
                f"Arrival: {aimed_arr}")


def main():
    """Main function to check train delays"""
    print("🚄 Checking UK train delays with TransportAPI...")
    
    try:
        app_id, app_key = get_api_credentials()
        from_station = os.getenv('FROM_STATION', 'CRE')
        to_station = os.getenv('TO_STATION', 'EUS')
        target_time = os.getenv('DEPARTURE_TIME')  # Optional
        operator_filter = os.getenv('OPERATOR_FILTER')  # Optional
        
        print(f"Checking trains from {from_station} to {to_station}")
        if operator_filter:
            print(f"Filtering by operator: {operator_filter}")
        
        # Get departures
        departures = get_train_departures(from_station, to_station, app_id, app_key)
        
        if departures is None:
            print("❌ Failed to get departures")
            return
        
        if len(departures) == 0:
            print("❌ No trains found")
            return
        
        # Find next train
        next_train = find_next_train(departures, target_time, operator_filter)
        
        if next_train:
            message = format_delay_message(next_train)
            print("\n" + message)
            
            # Create output file for GitHub Actions
            with open('train_status.txt', 'w') as f:
                f.write(message)
            
            # Set output variables for GitHub Actions
            with open(os.environ.get('GITHUB_OUTPUT', 'output.txt'), 'a') as f:
                f.write(f"message={message.replace('\n', '\\n')}\n")
                f.write(f"is_delayed={str(next_train.get('is_cancelled', False) or (next_train.get('expected_departure_time') != next_train.get('aimed_departure_time'))).lower()}\n")
                
                # Calculate delay minutes
                delay = 0
                if next_train.get('expected_departure_time') and next_train.get('aimed_departure_time'):
                    try:
                        aimed = datetime.datetime.strptime(next_train['aimed_departure_time'], '%H:%M')
                        expected = datetime.datetime.strptime(next_train['expected_departure_time'], '%H:%M')
                        delay = int(abs((expected - aimed).total_seconds() / 60))
                    except ValueError:
                        pass
                f.write(f"delay_minutes={delay}\n")
        else:
            print("❌ No matching train found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        with open('train_status.txt', 'w') as f:
            f.write(f"Error: {e}")


if __name__ == "__main__":
    main()
