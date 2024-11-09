use futures_util::sink::SinkExt;
use serde::{Deserialize, Serialize};
use tokio::net::TcpStream;
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message, tungstenite::Error};
use tui::layout::{Constraint, Direction, Layout};
use tui::style::{Color, Style};
use tui::text::{Span, Spans};
use tui::widgets::{Block, Borders};
use tui::{backend::CrosstermBackend, Terminal};

#[derive(Serialize, Deserialize, Debug)]
struct Portfolio {
    total_balance: f64,
    available_balance: f64,
    market_exposures: Vec<PortfolioMarketExposure>,
}

#[derive(Serialize, Deserialize, Debug)]
struct PortfolioMarketExposure {
    market_id: i64,
    position: f64,
    total_bid_size: f64,
    total_offer_size: f64,
    total_bid_value: f64,
    total_offer_value: f64,
}

#[derive(Serialize, Deserialize, Debug)]
struct Order {
    id: i64,
    market_id: i64,
    owner_id: String,
    transaction_id: String,
}

#[derive(Serialize, Deserialize, Debug)]
enum Side {
    UNKNOWN = 0,
    BID = 1,
    OFFER = 2,
}

async fn connect_websocket(url: &str) -> Result<(), Error> {
    let (mut ws_stream, _) = connect_async(url).await?;
    ws_stream
        .send(Message::Text("Hello WebSocket".to_string()))
        .await?;
    Ok(())
}

fn create_ui() -> Terminal<CrosstermBackend<std::io::Stdout>> {
    let stdout = std::io::stdout();
    let backend = CrosstermBackend::new(stdout);
    let terminal = Terminal::new(backend).unwrap();
    terminal
}

fn display_ui(terminal: &mut Terminal<CrosstermBackend<std::io::Stdout>>) {
    let size = terminal.size().unwrap();
    terminal
        .draw(|f| {
            let block = Block::default()
                .borders(Borders::ALL)
                .title("Portfolio Overview");
            f.render_widget(block, size);
        })
        .unwrap();
}

#[tokio::main]
async fn main() {
    // Example WebSocket URL
    let websocket_url = "wss://trading-bootcamp.fly.dev/api";

    // Connect to WebSocket
    if let Err(e) = connect_websocket(websocket_url).await {
        eprintln!("Error connecting to WebSocket: {}", e);
    }

    // Example data to display in terminal
    let portfolio = Portfolio {
        total_balance: 10000.0,
        available_balance: 5000.0,
        market_exposures: vec![PortfolioMarketExposure {
            market_id: 1,
            position: 100.0,
            total_bid_size: 200.0,
            total_offer_size: 150.0,
            total_bid_value: 5000.0,
            total_offer_value: 3000.0,
        }],
    };

    // Initialize the UI
    let mut terminal = create_ui();
    display_ui(&mut terminal);

    // Add more code here for interaction, updates, and rendering data (e.g., portfolio info, order books)
}
