"""
Main entry point for Purchase Bot.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from cli import SetupWizard
from scheduler import PurchaseScheduler
from app_paths import CONFIG_FILE


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Purchase Bot - Automate e-commerce purchases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py setup          # Interactive setup wizard
  python main.py run            # Start scheduler
  python main.py run --mode review  # Stop before final purchase click
  python main.py run --mode live    # Fully automated live mode
  python main.py run --dry-run      # Test without checkout actions
  python main.py run --interval 30  # Check every 30 seconds
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Setup command
    subparsers.add_parser(
        "setup",
        help="Interactive setup wizard for accounts and tasks"
    )
    
    # Run command
    run_parser = subparsers.add_parser(
        "run",
        help="Start the scheduler"
    )
    run_parser.add_argument(
        "--once",
        action="store_true",
        help="Run one check cycle and exit (used by GitHub Actions)"
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Alias for --mode dry-run"
    )
    run_parser.add_argument(
        "--mode",
        choices=["dry-run", "review", "live"],
        default="review",
        help="Execution mode (default: review)"
    )
    run_parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    run_parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True for speed, use --no-headless to see window)"
    )
    run_parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Show browser window (useful for debugging Walmart anti-bot detection)"
    )
    run_parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="HTTP proxy URL to avoid IP rate-limiting (e.g., http://proxy.example.com:8080)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "setup":
        wizard = SetupWizard()
        wizard.run()
    
    elif args.command == "run":
        scheduler = PurchaseScheduler()
        
        # Check if config exists
        if not CONFIG_FILE.exists():
            print("No configuration found!")
            print("   Run: python main.py setup")
            sys.exit(1)
        
        # Run scheduler with anti-bot flags
        try:
            if args.once:
                asyncio.run(scheduler.run_once(
                    dry_run=args.dry_run,
                    mode=args.mode,
                    headless=args.headless,
                    proxy=args.proxy,
                ))
            else:
                asyncio.run(scheduler.run_scheduler(
                    interval=args.interval,
                    dry_run=args.dry_run,
                    mode=args.mode,
                    headless=args.headless,
                    proxy=args.proxy,
                ))
        except KeyboardInterrupt:
            print("\n Shutting down...")
            sys.exit(0)


if __name__ == "__main__":
    main()
