#!/usr/bin/env python3
"""
Thermostat Test Application

A menu-driven script to interact with OJ Microline WiFi thermostats.
This script allows testing various thermostat operations before integration
with another project.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

from ojmicroline_thermostat import (
    OJMicroline, 
    WD5API, 
    WG4API, 
    Thermostat,
    OJMicrolineError,
    OJMicrolineAuthError,
    OJMicrolineConnectionError,
    OJMicrolineTimeoutError
)
from ojmicroline_thermostat.const import (
    REGULATION_SCHEDULE,
    REGULATION_MANUAL,
    REGULATION_COMFORT,
    REGULATION_VACATION,
    REGULATION_FROST_PROTECTION,
    REGULATION_BOOST,
    REGULATION_ECO
)

# Constants for preset modes
PRESET_MODES = {
    REGULATION_SCHEDULE: "Schedule",
    REGULATION_MANUAL: "Manual",
    REGULATION_COMFORT: "Comfort",
    REGULATION_VACATION: "Vacation",
    REGULATION_FROST_PROTECTION: "Frost Protection",
    REGULATION_BOOST: "Boost",
    REGULATION_ECO: "Eco"
}

class ThermostatApp:
    """Main application class for interacting with OJ Microline thermostats."""
    
    def __init__(self):
        """Initialize the application."""
        self.api = None
        self.thermostats: Dict[str, Thermostat] = {}
        self.config = {
            "model": None,
            "username": None,
            "password": None,
            "api_key": None,
            "customer_id": 99,
            "host": None
        }
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file if it exists."""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if value:  # Only set if value is not empty
                            self.config[key] = value
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
        with open(config_file, 'w') as f:
            for key, value in self.config.items():
                if value is not None:
                    f.write(f"{key}={value}\n")
    
    async def initialize_api(self) -> bool:
        """Initialize the API connection with the current configuration."""
        try:
            if self.config["model"] == "WD5 series":
                api_obj = WD5API(
                    username=self.config["username"],
                    password=self.config["password"],
                    api_key=self.config["api_key"],
                    customer_id=int(self.config.get("customer_id", 99))
                )
                if self.config["host"]:
                    api_obj.host = self.config["host"]
            elif self.config["model"] == "WG4 series":
                api_obj = WG4API(
                    username=self.config["username"],
                    password=self.config["password"]
                )
                if self.config["host"]:
                    api_obj.host = self.config["host"]
            else:
                print("Invalid model selected")
                return False
            
            self.api = OJMicroline(api=api_obj)
            await self.api.login()
            print("Successfully connected to the API")
            return True
        except OJMicrolineAuthError:
            print("Authentication error: Invalid credentials")
        except OJMicrolineConnectionError:
            print("Connection error: Could not connect to the API")
        except OJMicrolineTimeoutError:
            print("Timeout error: The API request timed out")
        except OJMicrolineError as e:
            print(f"Error initializing API: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return False
    
    async def fetch_thermostats(self) -> bool:
        """Fetch all thermostats associated with the account."""
        if not self.api:
            print("API not initialized. Please configure and connect first.")
            return False
        
        try:
            thermostats = await self.api.get_thermostats()
            self.thermostats = {t.serial_number: t for t in thermostats}
            return True
        except OJMicrolineError as e:
            print(f"Error fetching thermostats: {e}")
            return False
    
    def display_thermostats(self) -> None:
        """Display all thermostats and their basic information."""
        if not self.thermostats:
            print("No thermostats found. Try fetching them first.")
            return
        
        print("\n=== Thermostats ===")
        for idx, thermostat in enumerate(self.thermostats.values(), 1):
            online_status = "Online" if thermostat.online else "Offline"
            heating_status = "Heating" if thermostat.heating else "Not Heating"
            current_temp = thermostat.get_current_temperature() / 100
            target_temp = thermostat.get_target_temperature() / 100
            regulation_mode = PRESET_MODES.get(thermostat.regulation_mode, thermostat.regulation_mode)
            
            print(f"{idx}. {thermostat.name} ({thermostat.serial_number})")
            print(f"   Status: {online_status}, {heating_status}")
            print(f"   Temperature: Current {current_temp}°C, Target {target_temp}°C")
            print(f"   Mode: {regulation_mode}")
            print(f"   Model: {thermostat.model}")
            print(f"   Software Version: {thermostat.software_version}")
            print()
    
    async def display_thermostat_details(self, thermostat: Thermostat) -> None:
        """Display detailed information about a specific thermostat."""
        print(f"\n=== {thermostat.name} Details ===")
        print(f"Serial Number: {thermostat.serial_number}")
        print(f"Model: {thermostat.model}")
        print(f"Software Version: {thermostat.software_version}")
        print(f"Status: {'Online' if thermostat.online else 'Offline'}")
        print(f"Heating: {'Yes' if thermostat.heating else 'No'}")
        
        # Temperatures
        print(f"Current Temperature: {thermostat.get_current_temperature() / 100}°C")
        print(f"Target Temperature: {thermostat.get_target_temperature() / 100}°C")
        
        if thermostat.temperature_floor is not None:
            print(f"Floor Temperature: {thermostat.temperature_floor / 100}°C")
        if thermostat.temperature_room is not None:
            print(f"Room Temperature: {thermostat.temperature_room / 100}°C")
        
        print(f"Temperature Range: {thermostat.min_temperature / 100}°C - {thermostat.max_temperature / 100}°C")
        
        # Regulation mode
        regulation_mode = PRESET_MODES.get(thermostat.regulation_mode, thermostat.regulation_mode)
        print(f"Regulation Mode: {regulation_mode}")
        
        # Supported regulation modes
        supported_modes = [PRESET_MODES.get(mode, mode) for mode in thermostat.supported_regulation_modes]
        print(f"Supported Modes: {', '.join(supported_modes)}")
        
        # Additional features
        if hasattr(thermostat, 'adaptive_mode') and thermostat.adaptive_mode is not None:
            print(f"Adaptive Mode: {'Enabled' if thermostat.adaptive_mode else 'Disabled'}")
        
        if hasattr(thermostat, 'open_window_detection') and thermostat.open_window_detection is not None:
            print(f"Open Window Detection: {'Enabled' if thermostat.open_window_detection else 'Disabled'}")
        
        # Energy usage
        try:
            energy = thermostat.get_current_energy()
            if energy is not None:
                print(f"Energy Usage: {energy} kWh")
        except:
            pass
        
        # Time-based modes
        if thermostat.regulation_mode == REGULATION_BOOST and thermostat.boost_end_time:
            print(f"Boost End Time: {thermostat.boost_end_time}")
        
        if thermostat.regulation_mode == REGULATION_COMFORT and thermostat.comfort_end_time:
            print(f"Comfort End Time: {thermostat.comfort_end_time}")
        
        if thermostat.vacation_mode:
            if thermostat.vacation_begin_time:
                print(f"Vacation Begin Time: {thermostat.vacation_begin_time}")
            if thermostat.vacation_end_time:
                print(f"Vacation End Time: {thermostat.vacation_end_time}")
    
    async def set_temperature(self, thermostat: Thermostat) -> None:
        """Set the temperature for a specific thermostat."""
        print(f"\nCurrent target temperature: {thermostat.get_target_temperature() / 100}°C")
        print(f"Valid range: {thermostat.min_temperature / 100}°C - {thermostat.max_temperature / 100}°C")
        
        try:
            temp_input = input("Enter new temperature in °C (or press Enter to cancel): ")
            if not temp_input:
                print("Operation cancelled.")
                return
            
            temp = float(temp_input)
            temp_int = int(temp * 100)  # Convert to integer cents
            
            if temp_int < thermostat.min_temperature or temp_int > thermostat.max_temperature:
                print(f"Temperature must be between {thermostat.min_temperature / 100}°C and {thermostat.max_temperature / 100}°C")
                return
            
            # Ask for regulation mode
            print("\nSelect regulation mode:")
            print("1. Manual (permanent)")
            print("2. Comfort (temporary)")
            mode_choice = input("Enter choice (1-2, default: 1): ")
            
            regulation_mode = REGULATION_MANUAL
            duration = None
            
            if mode_choice == "2":
                regulation_mode = REGULATION_COMFORT
                duration_input = input("Enter duration in minutes (default: 60): ")
                duration = int(duration_input) if duration_input else 60
            
            await self.api.set_regulation_mode(
                resource=thermostat,
                regulation_mode=regulation_mode,
                temperature=temp_int,
                duration=duration
            )
            
            print(f"Temperature set to {temp}°C in {PRESET_MODES[regulation_mode]} mode")
            
            # Refresh thermostat data
            await asyncio.sleep(2)  # Wait for changes to propagate
            await self.fetch_thermostats()
            
        except ValueError:
            print("Invalid input. Please enter a valid temperature.")
        except OJMicrolineError as e:
            print(f"Error setting temperature: {e}")
    
    async def set_preset_mode(self, thermostat: Thermostat) -> None:
        """Set the preset mode for a specific thermostat."""
        print("\nAvailable preset modes:")
        
        # Display available modes
        modes = []
        for i, mode in enumerate(thermostat.supported_regulation_modes, 1):
            mode_name = PRESET_MODES.get(mode, mode)
            print(f"{i}. {mode_name}")
            modes.append(mode)
        
        try:
            choice = input("\nSelect mode (or press Enter to cancel): ")
            if not choice:
                print("Operation cancelled.")
                return
            
            mode_index = int(choice) - 1
            if mode_index < 0 or mode_index >= len(modes):
                print("Invalid selection.")
                return
            
            selected_mode = modes[mode_index]
            
            # Handle special cases for modes that need additional parameters
            if selected_mode == REGULATION_COMFORT:
                duration_input = input("Enter duration in minutes (default: 60): ")
                duration = int(duration_input) if duration_input else 60
                
                temp_input = input(f"Enter temperature in °C (default: {thermostat.get_target_temperature() / 100}°C): ")
                temp = int(float(temp_input) * 100) if temp_input else thermostat.get_target_temperature()
                
                await self.api.set_regulation_mode(
                    resource=thermostat,
                    regulation_mode=selected_mode,
                    temperature=temp,
                    duration=duration
                )
            elif selected_mode == REGULATION_MANUAL:
                temp_input = input(f"Enter temperature in °C (default: {thermostat.get_target_temperature() / 100}°C): ")
                temp = int(float(temp_input) * 100) if temp_input else thermostat.get_target_temperature()
                
                await self.api.set_regulation_mode(
                    resource=thermostat,
                    regulation_mode=selected_mode,
                    temperature=temp
                )
            elif selected_mode == REGULATION_VACATION:
                # Get vacation start and end times
                start_date_input = input("Enter vacation start date (YYYY-MM-DD, default: today): ")
                start_date = datetime.strptime(start_date_input, "%Y-%m-%d") if start_date_input else datetime.now()
                
                end_date_input = input("Enter vacation end date (YYYY-MM-DD): ")
                if not end_date_input:
                    print("End date is required for vacation mode.")
                    return
                end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
                
                temp_input = input("Enter temperature in °C (default: 15°C): ")
                temp = int(float(temp_input) * 100) if temp_input else 1500
                
                await self.api.set_vacation_mode(
                    resource=thermostat,
                    temperature=temp,
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                # For other modes, just set the mode
                await self.api.set_regulation_mode(
                    resource=thermostat,
                    regulation_mode=selected_mode
                )
            
            print(f"Mode set to {PRESET_MODES.get(selected_mode, selected_mode)}")
            
            # Refresh thermostat data
            await asyncio.sleep(2)  # Wait for changes to propagate
            await self.fetch_thermostats()
            
        except ValueError:
            print("Invalid input.")
        except OJMicrolineError as e:
            print(f"Error setting mode: {e}")
    
    async def configure_api(self) -> None:
        """Configure API connection details."""
        print("\n=== API Configuration ===")
        
        # Select thermostat model
        print("Select thermostat model:")
        print("1. WD5 series (OWD5, MWD5)")
        print("2. WG4 series (UWG4, AWG4)")
        
        model_choice = input("Enter choice (1-2): ")
        if model_choice == "1":
            self.config["model"] = "WD5 series"
        elif model_choice == "2":
            self.config["model"] = "WG4 series"
        else:
            print("Invalid choice. Configuration cancelled.")
            return
        
        # Get common credentials
        self.config["username"] = input("Username: ")
        self.config["password"] = input("Password: ")
        
        # Get model-specific details
        if self.config["model"] == "WD5 series":
            self.config["api_key"] = input("API Key: ")
            customer_id = input("Customer ID (default: 99): ")
            self.config["customer_id"] = customer_id if customer_id else "99"
        
        # Optional host
        host = input("Host (optional, leave blank for default): ")
        self.config["host"] = host if host else None
        
        # Save configuration
        self.save_config()
        print("Configuration saved.")
        
        # Test connection
        print("Testing connection...")
        if await self.initialize_api():
            await self.fetch_thermostats()
    
    async def select_thermostat(self) -> Optional[Thermostat]:
        """Let the user select a thermostat from the list."""
        if not self.thermostats:
            print("No thermostats found. Try fetching them first.")
            return None
        
        self.display_thermostats()
        
        if len(self.thermostats) == 1:
            # If there's only one thermostat, select it automatically
            return list(self.thermostats.values())[0]
        
        try:
            choice = input("Select thermostat (or press Enter to cancel): ")
            if not choice:
                return None
            
            index = int(choice) - 1
            thermostats_list = list(self.thermostats.values())
            
            if 0 <= index < len(thermostats_list):
                return thermostats_list[index]
            else:
                print("Invalid selection.")
                return None
        except ValueError:
            print("Invalid input.")
            return None
    
    async def main_menu(self) -> None:
        """Display and handle the main menu."""
        while True:
            print("\n=== Thermostat Test Application ===")
            print("1. Configure API Connection")
            print("2. Show Thermostats")
            print("3. View Thermostat Details")
            print("4. Set Temperature")
            print("5. Set Preset Mode")
            print("6. Refresh Thermostat Data")
            print("7. Exit")
            
            choice = input("\nEnter choice (1-7): ")
            
            if choice == "1":
                await self.configure_api()
            elif choice == "2":
                if not self.api:
                    print("API not initialized. Please configure and connect first.")
                    continue
                
                if not self.thermostats:
                    await self.fetch_thermostats()
                
                self.display_thermostats()
            elif choice == "3":
                if not self.api:
                    print("API not initialized. Please configure and connect first.")
                    continue
                
                if not self.thermostats:
                    await self.fetch_thermostats()
                
                thermostat = await self.select_thermostat()
                if thermostat:
                    await self.display_thermostat_details(thermostat)
            elif choice == "4":
                if not self.api:
                    print("API not initialized. Please configure and connect first.")
                    continue
                
                if not self.thermostats:
                    await self.fetch_thermostats()
                
                thermostat = await self.select_thermostat()
                if thermostat:
                    await self.set_temperature(thermostat)
            elif choice == "5":
                if not self.api:
                    print("API not initialized. Please configure and connect first.")
                    continue
                
                if not self.thermostats:
                    await self.fetch_thermostats()
                
                thermostat = await self.select_thermostat()
                if thermostat:
                    await self.set_preset_mode(thermostat)
            elif choice == "6":
                if not self.api:
                    print("API not initialized. Please configure and connect first.")
                    continue
                
                print("Refreshing thermostat data...")
                await self.fetch_thermostats()
                print("Data refreshed.")
            elif choice == "7":
                print("Exiting application.")
                break
            else:
                print("Invalid choice. Please try again.")

async def main():
    """Main entry point for the application."""
    app = ThermostatApp()
    await app.main_menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
