import requests
from bs4 import BeautifulSoup

class scrapper:
    def __init__(self,category,desiredPageCount):
        self.homePageLink = "https://www.n11.com"
        self.category=category
        self.targetDestination=self.homePageLink + "/" + self.category
        self.wholedata=[]
        self.currentPage=1
        self.pageCount=desiredPageCount

    def getCurrentDestination(self):
        if self.currentPage == 1:
            return self.targetDestination
        else:
            return self.targetDestination + "?pg=" + str(self.currentPage + 1)

    def getProductBrand(self,ProductFullName):
        spaceFoundIndex = 0
        for i in ProductFullName:
            if i == ' ':
                break
            else:
                spaceFoundIndex += 1
        return ProductFullName[0:spaceFoundIndex].replace('|','')

    def getProductFullName(self,data):
        return data.div.div.a.h3.text.strip().replace('|','')

    def getProductPrice(self,data):
        priceText = self.convertPriceTextToFloat(data.find("div", {"class": "proDetail"}).find("span", {"class", "newPrice cPoint priceEventClick"}).ins.text.strip(" TL\n")).replace('|','')
        return priceText

    def convertPriceTextToFloat(self,ProductPriceText):
        priceText = ""
        for i in ProductPriceText:
            if i != '.':
                priceText += i
        priceText = priceText.replace(',', '.')
        return priceText

    def getRating(self,data):
        ProductRatingText = data.span.get("class")[1].replace('|','')
        return ProductRatingText[1:]

    def getRatingCount(self,data):
        ProductRatingCountText = data.find("span", {"class": "ratingText"}).text.replace('|','')
        realPart = ProductRatingCountText[1:len(ProductRatingCountText) - 1]
        realPart = realPart.replace('.', '')
        return realPart

    def getProductDealer(self,data):
        return data.find("span", {"class": "sallerName"}).text.strip(" \n").replace('|','')

    def getDealerRating(self,data):
        return data.find("span", {"class": "point"}).text.strip(" \n")[1:].replace('|','')

    def getProductUrl(self,data):
        return data.find("a",{"class":"plink"})["href"]

    def getProductImageLink(self,data):

        return data.find("img",{"class":"lazy"})["data-original"]

    def getCategory(self):
        d=self.getCurrentDestination().split('/')
        return self.category

    def getAndWriteData(self,obj):
        while self.pageCount >= self.currentPage:
            try:
                currentLink = self.getCurrentDestination()
                htmlContent = requests.get(currentLink).content
                soup = BeautifulSoup(htmlContent, "html.parser")
                if soup.find("div", {"class": "listView"}) is not None:
                    listOfFoundData = soup.find("div", {"class": "listView"}).ul.find_all("li", {"class": "column"})
                else:
                    listOfFoundData = soup.find("section",
                                                {"class": "group listingGroup resultListGroup import-search-view"}).find(
                        "div", {"class": "catalogView"}).ul.find_all("li", {"class": "column"})
                separator = '|'
                for data in listOfFoundData:
                    ratingCont = data.find("div", {"class": "ratingCont"})
                    if ratingCont is not None:
                        try:
                            productFullName = self.getProductFullName(data)
                            productBrand = self.getProductBrand(productFullName)
                            productPrice = self.getProductPrice(data)
                            productRating = self.getRating(ratingCont)
                            productRatingCount = self.getRatingCount(ratingCont)
                            productDealer = self.getProductDealer(data)
                            dealerRating = self.getDealerRating(data)
                            productUrl=self.getProductUrl(data)
                            productImageLink=self.getProductImageLink(data)
                            self.wholedata.append(productBrand + separator + productFullName + separator + productPrice + separator + productRating + separator + productRatingCount + separator + productDealer + separator + dealerRating + separator + productUrl + separator + productImageLink)
                        except Exception as exc:
                            print(exc)
                            pass
                obj.progressChanged.emit(int(self.currentPage/self.pageCount*100))
                self.currentPage += 1
            except Exception as e:
                break