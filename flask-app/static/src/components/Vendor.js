import React from "react";

export default class Vendor extends React.Component {
  constructor(props) {
    super(props);
    
  }

  render() {
    const { name, branches, fooditems, drinks } = this.props.data;
    const servesDrinks = (
      <div className="row">
        <div className="icons">
          {" "}
          <i className="ion-wineglass"></i>{" "}
        </div>
        <div className="content">Serves Cold Drinks</div>
      </div>
    );

    return (
      <li onMouseEnter={this.props.handleHover.bind(null, name)} >
        <p className="truck-name">{name}</p>
        <div className="row">
          <div className="icons">
            {" "}
            <i className="ion-android-pin"></i>{" "}
          </div>
          <div className="content"> {branches.length} locations </div>
        </div>
        {drinks ? servesDrinks : null}
        <div className="row">
          <div className="icons">
            {" "}
            <i className="ion-fork"></i> <i className="ion-spoon"></i>
          </div>
          <div className="content">
            Serves {fooditems.join(", ")}
          </div>
        </div>
        <div className="row">
          <button className="orderButton" onClick={ () => { var myParams = { data: this.props.data }
                
                if (this.props.data != "") {
                  // axios.post('/truck/saveinfo', myParams)
                  // .then(function(){
                   window.location.href = "/placeOrder?key="+ name;
                  //Perform action based on response
                  // })
                  // .catch(function(error){
                  //   console.log(error);
                  // //Perform action based on error
                  // });
                } else {
                  alert("The data cannot be empty")
                } } }>
            Place Order
          </button>
        </div>
      </li>
    );
  }
}
